__all__ = ["AdapterCutter"]


class AdapterCutter:
    def __init__(self, start_adapter: str, end_adapter: str, min_len: int):
        self.start_adapter = start_adapter
        self.end_adapter = end_adapter
        self.min_len = min_len

    def get_cut_points(self, seq: str) -> tuple[int | None, int | None]:
        cut_from_start: int | None = None
        for i in range(0, len(self.start_adapter) - self.min_len - 1):
            if seq.startswith(self.start_adapter[i:]):
                cut_from_start = len(self.start_adapter[i:])
                break

        cut_from_end: int | None = None
        for i in range(len(self.end_adapter), self.min_len - 1, -1):
            if seq.endswith(self.end_adapter[:i]):
                cut_from_end = len(self.end_adapter) - len(self.end_adapter[:i])
                break
        return cut_from_start, cut_from_end
