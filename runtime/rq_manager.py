import threading
import zmq
import time
import copy
import math
import numpy as np
from colorama import Fore, Style

import runtime.common as common
from runtime.common import user_infos
from runtime.common import user_infos_lock
from runtime.common import rq_adjustment_period
from runtime.my_logger import My_Logger

class RQ_Manager(threading.Thread):
    def __init__(self, model, logger=None):
        super().__init__()
        self.model = model
        self.round_counter = 0
        self.backoff_round = -1
        self.backoff_count = 1
        self.logger = My_Logger() if logger is None else logger

        print(f"\n[RQ Manager] model {self.model.name}")


    def calculate_fps_score(self, fps_u):
        fps_u = min(fps_u, common.fps_upper)
        # FPS_score_u = math.log(min(FPS_cur, common.fps_upper)) / (math.log(common.fps_upper))
        return max( 0, 1 + (math.log(fps_u/common.fps_upper) / math.log(10)) )


    def run(self):
        while True:
            time.sleep(rq_adjustment_period)
            self.round_counter += 1

            if self.round_counter < self.backoff_round:
                print(f"[BACKOFF!!!!!!!] Round {self.round_counter} | Backoff Round {self.backoff_round} | Backoff Count {self.backoff_count}")
                continue

            print(f"\n[RQ Manager] Round {self.round_counter}")
            self.logger.log_to_file(f"{self.round_counter} ROUND\n")

            user_infos_lock.acquire()
            user_infos_copy = copy.deepcopy(user_infos)
            user_infos_lock.release()

            demotion_candidates = []
            promotion_candidates = []

            ##### 1. Find demotion/promotion candidates
            for user_info in user_infos_copy:
                print(f"\tUser {user_info.id} | QP {user_info.cq} | RQ {user_info.rq} | FPS {1000.0/user_info.avg_fl:.2f}")
                if user_info.avg_fl > -1:
                    if user_info.rq > 0:
                        demotion_candidates.append(user_info)
                    if user_info.rq < 3:
                        promotion_candidates.append(user_info)
                    user_info_log = user_info.get_user_info_message()
                    self.logger.log_to_file("\t" + user_info_log + "\n")

            ##### 2. Find a user to adjust RQ from demotion/promotion candidates
            user_to_adjust = None
            is_demote = False
            user_to_adjust = self.find_demote_user(demotion_candidates)
            if user_to_adjust is not None:
                is_demote = True
            else:
                user_to_adjust = self.find_promote_user(promotion_candidates)

            if user_to_adjust and common.backoff_switch == 1:
                self.address_rq_oscillation_by_exp_backoff(user_to_adjust, is_demote) # backoff

            ##### 3. Check the oscillation of RQ and backoff, and adjust RQ
            if user_to_adjust:
                if is_demote:
                    user_to_adjust.rq += -1
                else:
                    user_to_adjust.rq += 1

                user_to_adjust.record_rq(user_to_adjust.rq, self.round_counter)
                # Send new RQ to the RQ controller of an application
                new_rq = chr(user_to_adjust.rq)
                user_to_adjust.rq_socket.send(str.encode(new_rq))
                user_to_adjust.rq_socket.recv()

                # Update user-info table
                user_idx = user_to_adjust.id - 1
                user_infos_lock.acquire()
                user_infos[user_idx].update_runtime_info(user_to_adjust)
                user_infos_lock.release()


    def find_demote_user(self, demotion_candidates):
        print(f"[DEMOTE] Find Demote User among {len(demotion_candidates)}")
        if len(demotion_candidates) == 0:
            return None

        # check there is a user with FPS 30 or lower among demotion candidates
        is_under_fps = False
        for demotion_candidate in demotion_candidates:
            FPS_cur = 1000.0/float(demotion_candidate.avg_fl)
            FPS_thresh = 1000.0/float(demotion_candidate.slo_fl)
            if FPS_cur < 29:
                is_under_fps = True
                break

        if is_under_fps == False:
            print(f"\t[NONE] No user with FPS 30 or lower among demotion candidates.")
            return None

        demote_scores_u = []
        for demotion_candidate in demotion_candidates:
            FPS_cur = 1000.0/float(demotion_candidate.avg_fl)
            FPS_thresh = 1000.0/float(demotion_candidate.slo_fl)
            FPS_score_u = self.calculate_fps_score(fps_u=FPS_cur)

            # VQ Score
            VQ_u = self.model.predict_fq(demotion_candidate.codec, demotion_candidate.rq, demotion_candidate.cq)
            VQ_to_demote = self.model.predict_fq(demotion_candidate.codec, demotion_candidate.rq-1,
                                                demotion_candidate.cq)
            VQ_max = self.model.predict_fq(demotion_candidate.codec, 3, 10)
            VQ_min = self.model.predict_fq(demotion_candidate.codec, 0, 45)
            # print("VQ_u", VQ_u, "VQ_to_demote", VQ_to_demote, "VQ_max", VQ_max, "VQ_min", VQ_min)
            delta_VQ_u = abs(VQ_u - VQ_to_demote)
            VQ_score_u = delta_VQ_u / abs(VQ_max - VQ_min)

            score_u = (common.demote_weight*VQ_score_u) + ((1-common.demote_weight)*FPS_score_u)
            print(f"\tUser {demotion_candidate.id}| QP {demotion_candidate.cq} | RQ {demotion_candidate.rq} |  : FPS_score({FPS_score_u:.2f}), VQ_score({VQ_score_u:.2f}), Overall Score({score_u:.2f})")
            demote_scores_u.append(round(score_u, 3))

        if len(demote_scores_u) > 0:
            min_score_u = min(demote_scores_u)
            min_u = demote_scores_u.index(min_score_u)
            demote_user = demotion_candidates[min_u]
            print(f"[DEMOTE] user {demote_user.id} score_u {min_score_u:.2f}, RQ {demote_user.rq} -> {demote_user.rq-1}")
            return demote_user


    def find_promote_user(self, promotion_candidates):
        print(f"[PROMOTE] Find Promote User among {len(promotion_candidates)}")
        if len(promotion_candidates) == 0:
            return None

        promote_scores_u = []
        for promotion_candidate in promotion_candidates:
            FPS_cur = 1000.0/float(promotion_candidate.avg_fl)
            if FPS_cur < 33:
                print(f"There is a too tight user {promotion_candidate.id} with FPS {FPS_cur:.2f} -- SKIP PROMOTION")
                return None
            FPS_thresh = 1000.0/float(promotion_candidate.slo_fl)
            FPS_score_u = self.calculate_fps_score(fps_u=FPS_cur)

            # VQ Score
            VQ_u = self.model.predict_fq(promotion_candidate.codec, promotion_candidate.rq, promotion_candidate.cq)
            VQ_to_promote = self.model.predict_fq(promotion_candidate.codec, promotion_candidate.rq+1,
                                                  promotion_candidate.cq)
            VQ_max = self.model.predict_fq(promotion_candidate.codec, 3, 10)
            VQ_min = self.model.predict_fq(promotion_candidate.codec, 0, 45)
            # print(f"\tVQ_u {VQ_u:.2f}, VQ_to_promote {VQ_to_promote:.2f}, VQ_max {VQ_max:.2f}, VQ_min {VQ_min:.2f}")

            delta_VQ_u = abs(VQ_u - VQ_to_promote)
            VQ_score_u = delta_VQ_u / abs(VQ_max - VQ_min)

            score_u = (common.promote_weight*VQ_score_u) + ((1-common.promote_weight)*FPS_score_u)
            print(f"\tUser {promotion_candidate.id} | QP {promotion_candidate.cq} | RQ {promotion_candidate.rq} | : FPS_score({FPS_score_u:.2f}), VQ_score({VQ_score_u:.2f}), Overall Score({score_u:.2f})")
            promote_scores_u.append(round(score_u, 3))

        if len(promote_scores_u) > 0:
            max_score_u = max(promote_scores_u)
            max_u = promote_scores_u.index(max_score_u)
            promote_user = promotion_candidates[max_u]

            FPS_cur = 1000.0/float(promote_user.avg_fl)
            FPS_thresh = 1000.0/float(promote_user.slo_fl)
            if FPS_cur >= 30 + common.fps_buffer:
                print(f"[PROMOTE] user {promote_user.id} score_u {max_score_u:.2f}, RQ {promote_user.rq} -> {promote_user.rq+1}")
                return promote_user
            else:
                print(f"\t[PROMOTE] user {promote_user.id} score_u {max_score_u:.2f} but FPS {FPS_cur:.2f} is not enough.")
                return None


    def address_rq_oscillation_by_exp_backoff(self, user_to_adjust, is_demote):
        if len(user_to_adjust.rq_history) < 2:
            return

        user_prev_rq = user_to_adjust.rq_history[0][0]
        user_prev_round = user_to_adjust.rq_history[0][1]

        if is_demote == True:
            print(f"[Backoff] Demote: {user_to_adjust.rq-1} == {user_prev_rq}??")
            if user_to_adjust.rq-1 == user_prev_rq:
                print(f"[Backoff] Demote: {user_prev_round} > {self.round_counter - 5} or {user_prev_round} == -1??")
                if user_prev_round > self.round_counter - 5 or user_prev_round == -1: # 4 round window to check oscillation
                    self.backoff_round = self.round_counter + (common.backoff_base ** self.backoff_count)
                    self.backoff_count = min(self.backoff_count + 1, common.backoff_count_max)
                else:
                    self.backoff_count = 1 # not oscillating, collapse the backoff count

        if is_demote == False:
            print(f"[Backoff] Promote: {user_to_adjust.rq+1} == {user_prev_rq}??")
            if user_to_adjust.rq+1 == user_prev_rq:
                if user_prev_round > self.round_counter - 5 or user_prev_round == -1: # 4 round window to check oscillation
                    self.backoff_count = min(self.backoff_count + 1, common.backoff_count_max)
            else:
                self.backoff_count = 1 # not oscillating, collapse the backoff count

