#!/usr/bin/env python

import datetime

first = datetime.date(2019, 12, 31)

# ===================================================== fuzz the document names
with open('document-filenames', 'w') as _f:
    for _i in range(367):
        _f.write(f'{(first + datetime.timedelta(days=_i)).isoformat()}-upload.pdf\n')

# ========================================================== fuzz the usernames
with open('authors', 'r') as _fa:
    with open('usernames', 'w') as _fu:
        for _author in _fa:
            _firstname, _lastname = _author.split(".")
            _fu.write(f'{_lastname}')
            _fu.write(f'{_firstname}{_lastname}')
            _fu.write(f'{_firstname} {_lastname}')
            _fu.write(f'{_firstname}.{_lastname}')
            _fu.write(f'{_firstname[0]}{_lastname}')
            _fu.write(f'{_firstname[0]} {_lastname}')
            _fu.write(f'{_firstname[0]}.{_lastname}')
            _fu.write(f'{_lastname.lower()}')
            _fu.write(f'{_firstname.lower()}{_lastname.lower()}')
            _fu.write(f'{_firstname.lower()} {_lastname.lower()}')
            _fu.write(f'{_firstname.lower()}.{_lastname.lower()}')
            _fu.write(f'{_firstname[0].lower()}{_lastname.lower()}')
            _fu.write(f'{_firstname[0].lower()} {_lastname.lower()}')
            _fu.write(f'{_firstname[0].lower()}.{_lastname.lower()}')
