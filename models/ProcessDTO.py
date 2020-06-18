from models.ExecutionStat import ExecutionStat
from models.RepairedLine import RepairedLine
from models.FinancialStat import FinancialStat

import decimal
import logging

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("ProcessDTO")


class ProcessDTO:
    total_columns = 0
    total_threads = 1
    lines = []

    def __init__(self):
        self.current_line = ""
        self.line_number = 0
        self.thread_id = 0
        self.financial_stat = dict()
        self.execution_stat = ExecutionStat()

    def set_current_line(self, line_number):
        self.line_number = line_number
        self.current_line = ProcessDTO.lines[line_number]

    def add_repaired_line(self, repaired_line):
        log.warning("line %d has been repaired.", self.line_number + 1)
        self.execution_stat.repaired_lines.append(RepairedLine(self.line_number, repaired_line))

    def discard_current_line(self):
        log.warning("line %d has been discarded.", self.line_number + 1)
        self.execution_stat.discarded_lines.append(self.current_line)

    def is_empty(self):
        return not self.current_line

    def add_ok(self):
        self.execution_stat.processed += 1

    def update_financial_stat(self, gloss, amount, discount):
        stat = self.financial_stat.get(gloss, FinancialStat())
        stat.count += int(amount)
        stat.discount += decimal.Decimal(discount)
        self.financial_stat[gloss] = stat

    def merge_stats(self, other):
        self.execution_stat.merge(other.execution_stat)

        for key in other.financial_stat:
            if key in self.financial_stat.keys():
                self.financial_stat.get(key).merge(other.financial_stat.get(key))
            else:
                self.financial_stat[key] = other.financial_stat.get(key)

    def set_elapsed_time(self, elapsed_time):
        self.execution_stat.elapsed_time = elapsed_time
