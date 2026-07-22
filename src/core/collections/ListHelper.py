#  Created by:
#  mgr Artur Tomczak (artur.tomczak@fuw.edu.pl)
#  Intitute of Geophysiscs, Faculty of Physics, University of Warsaw

class ListHelper:
    @staticmethod
    def list_replace(lst: list, old, new):
        """replace list elements (inplace)"""
        return [new if x == old else x for x in lst]

    @staticmethod
    def to_string(lst: list, separator=", ") -> str:
        return separator.join(f"'{l}'" for l in lst)

    @staticmethod
    def find_duplicates(lst: list):
        """returns list of duplicated values"""
        seen = set()
        return [x for x in lst if x in seen or seen.add(x)]

    @staticmethod
    def get_differences(lst1: list, lst2: list):
        """returns difference between two lists
        Example:
        temp1 = ['One', 'Two', 'Three', 'Four']
        temp2 = ['One', 'Two']
        outputs: ['Three', 'Four']
        """
        return list(set(lst1) - set(lst2))

    @staticmethod
    def remove_elements(remove_from: list, elements_to_remove: list):
        """from one list removes elements of another list
        Example:
        l1 = ['One', 'Two', 'Three', 'Four', 'Four', 'One']
        l2 = ['One', 'Two']
        outputs: ['Three', 'Four', 'Four']
        """
        return [e for e in remove_from if e not in elements_to_remove]
