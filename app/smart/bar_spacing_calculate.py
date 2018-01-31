import math


class BarSpacingCalculator:
    def __init__(self, bar_gap, post_gap, bar_size):
        self.input_bar_size = bar_size
        self.input_between_posts = post_gap
        self.input_max_gap = bar_gap
        self.real_gap_size = round(self._gap(), 3)
        self._relative_tolerance = ((self.real_gap_size / 100) * .3) / 100
        self.real_center_to_center = round(self._center_to_center(), 3)
        self.real_edge_to_center = round(self._edge_to_center(), 3)
        self.real_No_bars = self._number_of_bars()
        self.fudge_center_to_center = self._rounding_function(self._center_to_center())
        self.fudge_edge_to_center_1 = self._rounding_function(self._edge_to_center())
        self.fudge_gap_size = self._rounding_function(self._gap())
        self.fudge_No_bars = self._number_of_bars()
        total = self.fudge_edge_to_center_1 + (self.fudge_center_to_center * self.fudge_No_bars)- (self.input_bar_size / 2)
        self.fudge_edge_to_center_2 = self._rounding_function(self.fudge_edge_to_center_1 - (self.input_between_posts - total))

    def _number_of_bars(self):
        return math.floor(self.input_between_posts / (self.input_max_gap + self.input_bar_size))

    def _gap(self):
        gap_spaces = self.input_between_posts - (self.input_bar_size * self._number_of_bars())
        return gap_spaces / (self._number_of_bars() + 1)

    def _center_to_center(self):
        return self._gap() + self.input_bar_size

    def _edge_to_center(self):
        return self._gap() + (self.input_bar_size / 2)

    def _close_upper_function(self):
        return math.isclose(math.ceil(self._gap()),
                            self._gap(),
                            rel_tol=self._relative_tolerance)

    def _close_lower_function(self):
        return math.isclose(math.floor(self._gap()),
                            self._gap(),
                            rel_tol=self._relative_tolerance)

    def _rounding_function(self, unit):
        if self._close_upper_function():
            return math.ceil(unit)
        elif self._close_lower_function():
            return math.floor(unit)
        else:
            return math.ceil(unit) - 0.5
