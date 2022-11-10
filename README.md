# tfutils
## A library for parsing Tracab soccer data from XML files.

Utilities to parse and plot soccer data from XML files 
provide by Tracab. Main features:
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
  
* Retains the methods and attributes of xml.etree.ElelemntTree.ElementTree,
  from which it inherits, allowing low-level access to the underlying data. 
  Example:
  ```
  home_team = source.find('HomeTeam')
  player = "Megan RAPINOE"
  query = ""Player/[@iPlayerId='{}']".format(player)
  team = source.find('HomeTeam')
  player_node = team.find(query)
  ```
At the moment only Tracab TF05 XML files are supported.

Typical usage:
```
from tfutils import TracabTF05Xml

source = TracabTF05XML('./data/my_tracab_tf05_file.xml')
source.parse()
source.summary() # prints a summary of the soccer match data

Source file: ./data/my_tracab_tf05_file.xml
Home team name and ID:Syria, 43838
Away team name and ID: Mauritania, 43870
Match date: 2021-12-06 18:00:00
Match ID: 129650
Match duration: 98.614 minutes

source.get_team_players('home')
```
![image](https://user-images.githubusercontent.com/2517549/200660485-7f08d43d-c667-4348-8187-d70e201d3810.png)
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
git clone git@github.com:your_fork/tfutils.git
cd tfutils
make install #or make dev-install for the dev version
# if you don't have make:
pip install . # or pip install -e . for the dev version
```
