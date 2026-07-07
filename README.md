# Postamat(MVP)
Project about placing orders by couriers in cells in postamat. Users can get placed order by receive code.
It contains API(by default localhost:port/api/postamat/) and Frontend(by default localhost:port/).

---

# Requirements
- Python 3.10+

Using isolated virtual environment is highly recommended.
_Project tested on mx linux with python 3.11 installed_

# Installation
1. clone repo:
```
git clone https://github.com/Vitek14/postamat.git
cd postamat
```

2. Create and activate venv:
```
python -m venv venv
source venv/bin/activate # Linux/macOS
# or
venv\Scripts\activate    # Windows
```

3. Install requirements:
```
pip install -r requirements.txt
```

**By default, project uses in memory db and applies all migrations by running server.**

---

# Usage
Run dev server:
```
python manage.py runserver 8001
```

---

# Tests
tests located at **postamat/tests** folder, so you can run them by using:
```
python manage.py test postamat/tests/
```
