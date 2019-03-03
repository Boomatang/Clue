import math


class BarSpacingCalculator:
    def __init__(self, bar_gap, post_gap, bar_size):
        self.input_bar_size = bar_size
        self.input_between_posts = post_gap
        self.input_max_gap = bar_gap
        self.real_gap_size = round(self._gap(), 3)
        self._relative_tolerance = ((self.real_gap_size / 100) * 0.3) / 100
        self.real_center_to_center = round(self._center_to_center(), 3)
        self.real_edge_to_center = round(self._edge_to_center(), 3)
        self.real_No_bars = self._number_of_bars()

    def _number_of_bars(self):
        try:
            return math.floor(
                self.input_between_posts / (self.input_max_gap + self.input_bar_size)
            )
        except ZeroDivisionError:
            return 0

    def _gap(self):
        if self._number_of_bars():
            gap_spaces = self.input_between_posts - (
                self.input_bar_size * self._number_of_bars()
            )
            return gap_spaces / (self._number_of_bars() + 1)
        else:
            return 0

    def _center_to_center(self):
        return self._gap() + self.input_bar_size

    def _edge_to_center(self):
        return self._gap() + (self.input_bar_size / 2)
