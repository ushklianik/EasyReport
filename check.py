from app.backend.validation import Nfr

obj = Nfr("default")
result = obj.compare_with_nfrs("DEMO", "20230824-1859-DEMO")
for r in result:
    print(r)
# obj.compare_with_nfrs("demo", "20230211-1106-demo")