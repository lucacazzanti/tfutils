# tfutils
## A library for parsing Tracab soccer data from XML files.

Utilities to parse, explore, and plot soccer data from XML files 
by data provider Tracab. Currently only TF05 XML files are supported. 
See also the [companion blog post](https://www.lucacazzanti.net/blog/posts/2022-11-15-tfutils/2022-11-15-tfutils.html)
Main features:

* Uses soccer sematics to access entitites like teams and players.
  Example:
  ```
  home_team = source.get_team('home')
  player = source.get_player('Lionel MESSI')
  ```
* Intuitive interface to plotting heatmaps for teams and players.
  Example:
  ```
  p = source.team_heatmap(team='home', hm_type='overall')
  ```
  ![image](https://user-images.githubusercontent.com/2517549/200660261-45efed04-8495-4faa-bc17-77b56bbd6559.png)
  
* Retains the methods and attributes of xml.etree.ElementTree.ElementTree,
  from which it inherits, allowing low-level access to the underlying data. 
  Example:
  ```
  home_team = source.find('HomeTeam')
  player = "Megan RAPINOE"
  query = ""Player/[@iPlayerId='{}']".format(player)
  team = source.find('HomeTeam')
  player_node = team.find(query)
  
  # ... gives the same result as
  player = " Megan RAPINOE"
  source.get_player(player)
  ```
At the moment only Tracab TF05 XML files are supported.

Typical usage:
```
from tfutils import TracabTF05Xml

# Parse and get basic facts about the macth
source = TracabTF05XML('./data/my_tracab_tf05_file.xml')
source.parse()
source.summary() # prints a summary of the soccer match data

Source file: ./data/my_tracab_tf05_file.xml
Home team name and ID:Syria, 43838
Away team name and ID: Mauritania, 43870
Match date: 2021-12-06 18:00:00
Match ID: 129650
Match duration: 98.614 minutes

# List of players ...
source.get_team_players('away')
{'id': ['431494',
  '391160',
  '431495',
  '433176',
  '436778',
  '431501',
  '393847',
  '431516',
  '395993',
  '431489',
  '392901',
  '431511',
  '431500',
  '433659',
  '431488'],
 'jersey': ['1',
  '2',
  '3',
  '4',
  '6',
  '7',
  '8',
  '9',
  '10',
  '12',
  '14',
  '17',
  '18',
  '21',
  '23'],
 'name': ["M'backe N'DIAYE",
  'El Mostapha DIAW',
  'Mohamedhen BEIBOU',
  'Harouna ABOU',
  'Gussouma FOFANA',
  'Idrissa THIAM',
  'Amadou NIASS',
  'Hemeya TANJI',
  'Adama BÀ',
  'Alassane DIOP',
  'Mohamed Dellah YALY',
  'Demba TRAWRE',
  'Mouhsine BODDA',
  'Ablaye SY',
  'Mohamed SOUEID']}

# ... you can also use the team name itself and put the resulting dictionary in a dataframe
team_players = source.get_team_players('Mauritania')
players_df = pd.DataFrame.from_dict(players)
players_df
```
![image](https://user-images.githubusercontent.com/2517549/201769043-a0fbd8cb-f1ac-4788-86eb-0408667dd373.png)

```
p = source.team_possession_heatmap(team='away', hm_type='first-half')
```
![image](https://user-images.githubusercontent.com/2517549/200660885-69e652e1-56b0-4cc2-8045-f3f7cfb91b82.png)
```
p = source.player_heatmap(player='431495')
```
![image](https://user-images.githubusercontent.com/2517549/200661408-abe482da-8885-4bbc-8d6b-17a40f46d7c8.png)

## Installation
```
> git clone git@github.com:your_fork/tfutils.git
> cd tfutils
> pip install -r requirements.txt .

# ... or, to install the dev version:
> pip install -r requirements.txt -e .
 
# If you prefer make:
> make install 
# ... or ...
> make dev-install
```
