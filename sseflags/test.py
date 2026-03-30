from sys import float_info

from . import set_flags, get_flags, Flags


def run() -> None:
    """
    Basic tests to check the DAZ and FTZ flags and their effect on operations
    involving subnormal numbers.

    n is the smallest normal number, s = n / 2 is a subnormal number;
    the operation s * 2 should produce a normal number (or zero with DAZ),
    the operation n / 2 should produce a subnormal number (or zero with FTZ).
    """
    if not set_flags(daz=False, ftz=False):
        print('Setting DAZ/FTZ is not implemented.')
        return

    n = float_info.min
    s = n / 2
    print(f'{n = :g}\n{s = :g}')

    for daz, ftz in [(False, False), (False, True),
                     (True, False), (True, True)]:
        flags: Flags = {'daz': daz, 'ftz': ftz}
        print(f'\nSet: {flags},\ngot: ', end='')
        if not set_flags(**flags):
            print('not supported.')
            continue
        print(get_flags())
        s2 = s * 2
        n2 = n / 2
        set_flags(daz=False, ftz=False)
        print(f's * 2 = {s2:g}\nn / 2 = {n2:g}')


if __name__ == '__main__':
    run()
