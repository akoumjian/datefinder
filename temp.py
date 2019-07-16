from datefinder import find_dates
import datefinder

dt = datefinder.DateFinder()

# result = find_dates('19th day of May, 2015', strict=True)

# result = find_dates('May 20th 2015', strict=True)

# result = find_dates('May 20 2015', strict=True)

result = dt.extract_date_strings('May 20th 2015', strict=True)
result = dt.extract_date_strings('May 20 2015', strict=True)



print(list(result))