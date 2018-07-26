from csv import DictReader
from pathlib import Path as P

from app.models import BomFile, BomFileContents, BomSession
from app.utils import isFloat, isInt

DESC = 'DESCRIPTION'
PLATE = 'PL'
LENGTH = 'LENGTH'
QTY = 'QTY.'
ITEM = 'ITEM NO.'

TOTAL = 'total'


class BOM:

    def __init__(self, file_name, ref=None):
        self.massages = []
        self.ref = ref
        self.data = []
        self.beam_data = {}
        self.stock = {}
        self.cut_beams = {}
        self.error = 50
        self.total_qty = 1
        self.read_csv(file_name)
        self.setup()

    def read_csv(self, file_name):
        f = DictReader(open(file_name))
        for row in f:
            self.data.append(row)
        del f

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

                self._has_total(item)

                if isFloat(item[LENGTH]):
                    length = int(float(item[LENGTH]))
                else:
                    length = int(item[LENGTH])
                qty = int(item[QTY]) * self.total_qty
                mark = item[ITEM]
                self.beam_data[item[DESC]].append({LENGTH: length, QTY: qty, ITEM: mark})

    def _has_total(self, item):
        first = True

        if self.total_qty > 1:
            first = False

        for key in item.keys():
            if key.lower() == TOTAL:
                temp = int(item[key])
                qty = int(item[QTY])
                self.total_qty = temp / qty

                if self.total_qty > 1 and first:
                    first = False
                    self.massages.append((f'Looks like the total unit quantity is more that one. '
                                          f'The total unit quantity been used is {int(self.total_qty)}', 'General'))

    def _add_beam_to_stock(self, beam):
            # for row in values:
            #     print(row)
        stock = beam[0]
        length, qty = self._get_stock_data(beam[1])
        if length is not None:
            self.stock[stock][length] = qty

    @staticmethod
    def _get_stock_data(beam):
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
                waste = i - beam_usage + self.error
                if len(cut_beam) > 0:
                    self.cut_beams[beam]['cut'][i].append((cut_beam, beam_usage, int(waste)))
                t += 1

        for part in work:
            if part[QTY] > 0:
                self.cut_beams[beam]['left'].append(part)

    def set_saw_error_value(self, value):
        self.error = value


class RawBomFile:

    ITEM_NO = 'ITEM NO.'
    PART_NUMBER = 'PART NUMBER'
    DESCRIPTION = 'DESCRIPTION'
    BB_LENGTH = '3D-Bounding Box Length'
    BB_WIDTH = '3D-Bounding Box Width'
    BB_THICKNESS = '3D-Bounding Box Thickness'
    LENGTH = 'LENGTH'
    QTY = 'QTY.'

    def __init__(self, file):
        self.file = P(file)

        self.entry = BomFile(name=self.file.name)
        self.setup()

    def setup(self):

        with open(self.file, encoding='ISO-8859-1') as f:
            data = DictReader(f)
            for row in data:
                value = self._convert_data(row)
                item = self._add_value_to_db(value)
                self._add_value_to_entry(item)
        # add items to the  bom file
        # Check that all formats
        # find child parents

    def return_entry(self):
        return self.entry

    def _read_csv(self):
        with open(self.file, 'r') as f:
            values = DictReader(f, encoding='ISO-8859-1')
            print(values)
            # for row in values:
            #     print(row)

    def _add_value_to_entry(self, value):
        self.entry.items.append(value)

    def _add_value_to_db(self, value):
        item = BomFileContents()
        item.item_no = value[self.ITEM_NO]
        item.part_number = value[self.PART_NUMBER]
        item.description = value[self.DESCRIPTION]
        item.BB_length = value[self.BB_LENGTH]
        item.BB_width = value[self.BB_WIDTH]
        item.BB_thickness = value[self.BB_THICKNESS]
        item.length = value[self.LENGTH]
        item.qty = value[self.QTY]
        item.parent = None

        return item

    def _convert_data(self, data):
        data[self.ITEM_NO] = self._check_is_string(data[self.ITEM_NO])
        data[self.PART_NUMBER] = self._check_is_string(data[self.PART_NUMBER])
        data[self.DESCRIPTION] = self._check_is_string(data[self.DESCRIPTION])

        data[self.BB_LENGTH] = self._check_is_float(data[self.BB_LENGTH])
        data[self.BB_WIDTH] = self._check_is_float(data[self.BB_WIDTH])
        data[self.BB_THICKNESS] = self._check_is_float(data[self.BB_THICKNESS])
        data[self.LENGTH] = self._check_is_float(data[self.LENGTH])

        data[self.QTY] = self._check_is_int(data[self.QTY])

        return data

    @staticmethod
    def _check_is_string(string):
        value = string.strip()

        if len(value) > 0:
            return value
        else:
            return None

    @staticmethod
    def _check_is_float(num):

        value = RawBomFile._check_is_string(num)

        if isFloat(value):
            return float(value)
        else:
            return None

    @staticmethod
    def _check_is_int(num):

        value = RawBomFile._check_is_string(num)

        if isInt(value):
            return int(value)
        else:
            return None


class CreateBom:
    """
        data_store = {'50x50': [{'item': '1.1',
                                 'description': '50x50',
                                 'length': 500,
                                 'total': 10,
                                 'missing': 10,
                                 'cuttable': True}],
                      'unused': [{'item': '1.1',
                                  'description': 'Floor Panel',
                                  'length': 500,
                                  'total': 10,
                                  'missing': 10,
                                  'cuttable': True}]
                     }
        beam = {'description': '50x50',
                'length': 6500,
                'items': [],
                'waste': 500,
                'percent': 90}
        """

    def __init__(self, setup, data):
        self.data: BomFile = BomFile.query.filter_by(id=data).first()
        self.setup: BomSession = BomSession.query.filter_by(id=setup).first()
        self.data_store = {'unused': []}
        self.beams = {}
        self.un_cut_parts = []

    def run(self):
        self._setup_data_store_basic_information()
        self._setup_parts_for_cutting()
        self._create_cutting_list()

    def _setup_data_store_basic_information(self):
        for size in self.setup.sizes:
            self.data_store[size.size] = []

    def _setup_parts_for_cutting(self):
        self._add_parts_to_data_store()
        self._sort_parts_by_length()

    def _add_parts_to_data_store(self):
        for item in self.data.items:
            total = item.total_required()
            value = {'item': item.item_no,
                     'description': item.description,
                     'length': item.length,
                     'total': total,
                     'missing': total,
                     'cuttable': True}
            if value['description'] in self.data_store.keys():
                self.data_store[value['description']].append(value)
            else:
                self.data_store['unused'].append(value)

    def _sort_parts_by_length(self):
        for size in self.setup.sizes:
            if size.size == 'unused':
                break

            items = self.data_store[size.size]
            items.sort(key=self.item_length)
            items.reverse()
            self.data_store[size.size] = items

    @staticmethod
    def item_length(x):
        """This is a helper method"""
        try:
            return float(x['length'])
        except TypeError:
            return 0

    def _create_cutting_list(self):

        for size in self.setup.sizes:
            self.parts = self.data_store.get(size.size)
            if size.size == 'unused':
                break

            self.beams[size.size] = []

            counter = self._total_number_of_parts()

            while counter:
                entry, count = self._create_beam(size.default)
                if entry is not None:
                    self.beams[size.size].append(entry)
                counter -= count

    def _create_beam(self, size):
        beam = {'length': size,
                'items': {}}
        beam_length = beam['length']

        counter = 0
        for part in self.parts:
            short = False
            while self._part_is_usable(part) and not short:
                if part['length'] is not None:
                    if part['length'] > beam['length']:
                        beam['length'] = self._get_next_beam_length(part)
                        beam_length = beam['length']

                    if beam['length'] is None:
                        part['cuttable'] = False
                        self.un_cut_parts.append(part)
                        return None, part['missing']

                    if (beam_length - part['length']) >= 0:

                        key, value = self._create_item_for_beam(part)

                        if key in beam['items']:

                            beam['items'][key]['qty'] += 1
                        else:
                            beam['items'][key] = value
                        beam_length -= part['length']
                        part['missing'] -= 1
                        counter += 1
                    else:

                        short = True
                else:
                    part['cuttable'] = False
                    self.un_cut_parts.append(part)
                    counter += part["missing"]

        beam['waste'] = int(beam_length)
        output = beam

        return output, counter

    @staticmethod
    def _part_qty(part):
        if part['missing'] > 0:
            return True
        else:
            return False

    @staticmethod
    def _create_item_for_beam(part):

        key = part['item']
        value = {
            'item': part['item'],
            'description': part['description'],
            'length': part['length'],
            'qty': 1
        }
        return key, value

    def _get_next_beam_length(self, part):

        for size in self.setup.sizes:

            if size.size == part['description']:
                lengths = []
                for item in size.lengths:
                    lengths.append(item.length)

                lengths.sort()

                for length in lengths:
                    if length > part['length']:
                        return length

        return None

    def _total_number_of_parts(self):
        count = 0
        for item in self.parts:
            count += item['total']

        return count

    @staticmethod
    def _is_cuttable(part):
        return part['cuttable']

    def _part_is_usable(self, part):
        if self._part_qty(part) and self._is_cuttable(part):
            return True
        else:
            return False
