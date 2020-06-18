class ExecutionStat:
    """Estadística de ejecución."""

    def __init__(self):
        self.processed = 0
        self.discarded_lines = []
        self.repaired_lines = []
        self.elapsed_time = 0
        pass

    def merge(self, other):
        self.processed += other.processed
        self.discarded_lines.extend(other.discarded_lines)
        self.repaired_lines.extend(other.repaired_lines)

    def get_total_processed(self):
        return self.processed + len(self.discarded_lines)
