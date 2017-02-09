13_cinemas
===================

The script cinemas.py parses [movie poster](http://www.afisha.ru/msk/schedule_cinema/) and gets 10 last movies on poster that stay in Moscow theaters for now.

Then it fetches the rating of each movie from kinopoisk. 

Afterwards, the script outputs the movie titles with their ratings and theaters numbers in descending order of rating. 

How to run
----------
Clone this repository. Then go to the repository directory.

Install all requirements:
```
pip3 install -r requirements.txt
```
Run the script:
```
python3 cinemas.py
```

Usage
-----

```
~$ python3 cinemas.py
Proxies are collected!
Parsing... Stand by.
100% (10 of 10) |#########################| Elapsed Time: 0:01:22 Time: 0:01:22
№    Title                         Kinopoisk rating    Theaters number               

1    Ла-Ла Ленд                    8.441               65                            
2    Идеальные незнакомцы          7.522               45                            
3    Голос монстра                 7.484               99                            
4    Балерина                      7.049               98                            
5    Притяжение                    6.641               162                           
6    Космос между нами             6.56                75                            
7    Отпетые напарники             5.936               63                            
8    Три икса: Мировое господство  5.66                37                            
9    Звонки                        4.778               130                           
10   На пятьдесят оттенков темнее  No info             156   
```
