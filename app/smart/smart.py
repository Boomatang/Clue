from csv import DictReader

DESC = 'DESCRIPTION'
PLATE = 'PL'
LENGTH = 'LENGTH'
QTY = 'QTY.'
ITEM = 'ITEM NO.'


class BOM:

    def __init__(self, file_name, ref=None):
        self.ref = ref
        self.data = []
        self.beam_data = {}
        self.stock = {}
        self.cut_beams = {}
        self.error = 50
        self.read_csv(file_name)
        self.setup()

    def read_csv(self, file_name):
        f = DictReader(open(file_name))
        for row in f:
            self.data.append(row)
        del(f)

    def setup(self):
        self._get_beam_types()
        self._sort_data()
        self._required_stock()


    def keys(self):
        return self.beam_data.keys()

    def update_stock(self, beam):

        if beam[0] in self.keys():
            self._add_beam_to_stock(beam)

    def _get_beam_types(self):
        for item in self.data:
            description = item[DESC]
            if PLATE not in description:
                self._inlist(description)

    def _sort_data(self):
        for item in self.data:
            if item[DESC] in self.beam_data.keys():
                length = int(item[LENGTH])
                qty = int(item[QTY])
                mark = item[ITEM]
                self.beam_data[item[DESC]].append({LENGTH: length, QTY: qty, ITEM: mark})

    def _add_beam_to_stock(self, beam):
        stock = beam[0]
        length, qty = self._get_stock_data(beam[1])
        if length is not None:        
            self.stock[stock][length] = qty

    def _get_stock_data(self, beam):
        if len(beam) > 0:
            value = beam.lower()
            value = value.split('x')
            length = int(value[0])
            qty = int(value[1])
            return length, qty

        else:
            return None, None

    def _inlist(self, name):
        if name not in self.beam_data.keys():
            self.beam_data[name] = []

    def _required_stock(self):
        for key in self.keys():
            self.stock[key] = {}
            self.cut_beams[key] = {}

    def create_results(self):
        beam_lengths = self._sorted_stock_beam_lengths()
        self._sort_beam_lengths()
        for key in beam_lengths.keys():
            self._do_math(beam=key, order=beam_lengths[key])

    def _sorted_stock_beam_lengths(self):
        temp = {}
        for key in self.keys():
            temp[key] = []
            for k in self.stock[key].keys():
                temp[key].append(int(k))
            temp[key].sort(reverse=True)
        return temp

    def _sort_beam_lengths(self):

        def length_sort(x):
            return int(x[LENGTH])

        for key in self.beam_data.keys():
            self.beam_data[key].sort(key=length_sort)
            self.beam_data[key].reverse()

    def _do_math(self, beam=None, order=None):
        work = self.beam_data[beam]
        stock = self.stock[beam]
        self.cut_beams[beam] = {'cut': {}, 'left': []}

        for i in order:
            # print(f'stock length is {i} and there is {stock[i]} of them')
            t = 0
            self.cut_beams[beam]['cut'][i] = []
            while t < stock[i]:

                cut_beam = []
                beam_length = i - self.error
                # print(beam_length, type(beam_length))
                for part in work:
                    run = True
                    while run:
                        if part[QTY] > 0:
                            if (beam_length - part[LENGTH]) >= 0:
                                cut_beam.append(part)
                                beam_length = beam_length - part[LENGTH]
                                part[QTY] = part[QTY] - 1
                            else:
                                run = False
                        else:
                            run = False
                beam_usage = (i - beam_length)
                if len(cut_beam) > 0:
                    self.cut_beams[beam]['cut'][i].append((cut_beam, beam_usage))
                t += 1

        for part in work:
            if part[QTY] > 0:
                self.cut_beams[beam]['left'].append(part)

