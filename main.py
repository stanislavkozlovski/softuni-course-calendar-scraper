from extract_course_info import extract_course_info
def main():
    url = 'https://softuni.bg/trainings/1390/software-technologies-june-2016'
    #url = 'https://softuni.bg/trainings/1459/drupal-8-site-building-october-2016'
    #url = 'https://softuni.bg/trainings/1425/web-fundamentals-html-css-august-2016'
    #url = 'https://softuni.bg/trainings/1374/c-sharp-advanced-oop-july-2016'
    #url = 'https://softuni.bg/trainings/1403/electronics-basics-july-2016'
    #url = 'https://softuni.bg/trainings/1463/express-js-development-october-2016'
    #url = 'https://softuni.bg/trainings/1447/js-fundamentals-september-2016'
    #url = 'https://softuni.bg/trainings/1434/node-js-development-september-2016'
    #url = 'https://softuni.bg/trainings/1435/javaee-fundamentals-september-2016'
    #url = 'https://softuni.bg/trainings/1449/databases-basics-sqlserver-september-2016'
    # TODO: Validate URL
    print(extract_course_info(url))


if __name__ == '__main__':
    main()





