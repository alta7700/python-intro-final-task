## Установить зависимости
`poetry install`
или 
`pip install -r requirements.txt`

# Fastq analyzer
### Посмотреть возможные параметры
`python main.py fastq --help`

### Запустить тестовый скрипт с файлом, находящимся в папке test_data
`python main.py fastq -d fastq_analyzer/test_data -n READS055722.student_13.fastq`

### Исключить адаптерные последовательности с минимальным вхождением 8
`python main.py fastq -d fastq_analyzer/test_data -n READS055722.student_13.fastq --remove-adapters 8`

### Выбрать файл с адаптерной последовательностью
`python main.py fastq -d fastq_analyzer/test_data -n READS055722.student_13.fastq --remove-adapters 8 -a some-other-adapter.txt`

### Установить адаптерную последовательность последовательность (--adapter-seq)
`python main.py fastq -d fastq_analyzer/test_data -n READS055722.student_13.fastq --remove-adapters 8 --adapter-seq GTAGTAACTTAAAGAAGGAAATTCTGACACATGCTACA`

### Установить разные начальные и концевые адаптерные последовательности
Или можно поместить в папку с данными файлы start-adapter.txt и end-adapter.txt  
Их также можно указать именами файлов с помощью --start-adapter и --end-adapter  
`python main.py fastq -d fastq_analyzer/test_data -n READS055722.student_13.fastq --remove-adapters 8 --start-adapter-seq GTAGTAACTTAAAGAAGGAAATTCTGACACATGCTACA --end-adapter-seq GATCGGAAGAGCACACGTCTGAACTCCAGTCACAGGTTATCATCTCGTAT`

### Вывести графики в subplot (--subplot)
`python main.py fastq -d fastq_analyzer/test_data -n READS055722.student_13.fastq --subplot`

### Установить качество графиков (--charts-quality/-cq)
`python main.py fastq -d fastq_analyzer/test_data -n READS055722.student_13.fastq --charts-quality 600`

# GEO parser
### В параметры передать просто все ссылки, которые хотите распарсить
`python main.py geo "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSM357351"`
