"""A library for parsing Tracab XML files of soccer data.

Provides set of utilities to parse and plot soccer data 
provided by Tracab in XML files. Main features:
* Uses soccer sematics to access entitites like teams and players.
Example: 
home_team = source.get_team('home')
player = source.get_player('Lionel MESSI')
* Intuitive interface to plotting heatmaps for teams and players.
Example:
source.player_possession_heatmap(player='12345', possession='in')
source.team_heatmap(team='home', hm_type='attack')
* Retains the methods and attributes of xml.etree.ElelemntTree.ElementTree,
from which it inherits, allowing low-level access to the underlying data. 
    
At the moment only Tracab TF05 XML files are supported.

Typical usage:
from tfutils import TracabTF05Xml

source = TracabTF05XML('./data/my_tracab_tf05_file.xml')
source.parse()
source.summary() # prints a summary of the soccer match data

source.get_team_players('home')
source.team_heatmap(team='home', hm_type='attack')
source.player_possession_heatmap(player='12345', possession='in')
"""  

from typing import Tuple, Union
from xml.etree.ElementTree import Element, ElementTree

import matplotlib.pyplot as plt
import mplsoccer as mpl
import numpy as np


class TracabTf05Xml(ElementTree):
    """Tracab TF05 XML file parser and plotter.
    
    Inherits from xml.etree.ElementTree.ElementTree and expands it with 
    a soccer-specific API for extracting team and player information, and
    for plotting corresponding team-level and player-level heatmaps.

    Relies on (but does not inherit from) mplsoccer.Pitch(), pandas, and matplotlib. 
    
    Attributes:
        pitch_length: the length of the soccer pitch to use as input to Pitch() (default is 105)
        pitch_width: the width of the soccer pitch to use as input to Pitch() (deafult is 68)
        pitch_type: the type of soccer pitch to use as input to Pitch() (default is 'skillcorner')
    
    Attributes:
        f05_fname:
        match_id:
        home_team_name:
        home_team_id:
        away_team_name:
        away_team_id:
        match_duration:
        arena_name:
        arena_id:
        competion_name:
        competition_id:
        match_date:
        season:
        season_id:
        sport_id:
        sport_name:    
    """
    
    def __init__ (self, tf05_fname: str, pitch_length: float = 105, pitch_width: float = 68, pitch_type: str = 'skillcorner') -> None:
        """Initializer for TracabTf05Xml class."""

        # These are the only public attibutes
        self.pitch_length = pitch_length
        self.pitch_width = pitch_width
        self.pitch_type = pitch_type
        
        # The source file is set once and for all (final static)
        self.__tf05_fname = tf05_fname

        # These will be set in parse()  
        self.__match_id = None
        self.__home_team_name = None
        self.__home_team_id = None
        self.__away_team_name = None
        self.__away_team_id = None
        self.__match_duration = None
        self.__arena_name = None
        self.__arena_id = None
        self.__competion_name = None
        self.__competition_id = None
        self.__match_date = None
        self.__season = None
        self.__season_id = None
        self.__sport_id = None
        self.__sport_name = None

        # Heatmap dimensions according to Tracab format
        self.__HM_WIDTH = 14 #y axis
        self.__HM_LENGTH = 20 #x axis
        
        # Translators English <-> XML element tag
        self.__team_heatmap_dict = {'overall': 'sHeatmap',
                                  'defence': 'sDefenceHeatmap',
                                  'midfield': 'sMidfieldHeatmap',
                                  'attack': 'sAttackHeatmap'}
        self.__possession_heatmap_dict = {'overall': 'sHeatmap',
                                          'first-half': 'sFirstHalfHeatmap',
                                          'second-half': 'sSecondHalfHeatmap'}
        self.__team_dict = {'home': 'HomeTeam', 'away': 'AwayTeam'}
        
        # Defaults for plotting the pitch and the heatmap
        self.__default_pitch_kwargs = {'line_zorder': 2, 'pitch_color': '#22312b', 'line_color': 'black'}
        self.__default_heatmap_kwargs = {'cmap': 'Blues'}
        # These come straight from a pitch.grid() example on mplsoccer
        self.__default_grid_kwargs = {'endnote_height': 0.03, 'endnote_space': 0,
            'grid_width': 0.88, 'left': 0.025, 'title_height': 0.06, 'title_space': 0,
            'axis': False, 'grid_height': 0.86, 'figheight': 6.5}
        
        ElementTree.__init__(self)
        
    # We want the top-level match data accessible, but not editable: use properties 
    
    @property
    def match_id(self) -> str:
        return self.__match_id
    @property
    def tf05_fname(self) -> str:
        return self.__tf05_fname
    @property
    def home_team_name(self) -> str:
        return self.__home_team_name
    @property
    def home_team_id(self) -> str:   
        return self.__home_team_id
    @property   
    def away_team_name(self) -> str:
        return self.__away_team_name
    @property
    def away_team_id(self) -> str: 
        return self.__away_team_id
    @property
    def match_duration(self) -> str:    
        return self.__match_duration
    @property
    def arena_name(self) -> str:  
        return self.__arena_name
    @property
    def arena_id(self) -> str:   
        return self.__arena_id
    @property
    def competition_name(self) -> str:    
        return self.__competion_name
    @property
    def competition_id(self) -> str:
        return self.__competition_id
    @property
    def match_date(self) -> str:
        return self.__match_date
    @property
    def season(self) -> str:    
        return self.__season
    @property
    def season_id(self) -> str:    
        return self.__season_id
    @property
    def sport_id(self) -> str:    
        return self.__sport_id
    @property
    def sport_name(self) -> str:
        return self.__sport_name
    
    def default_kwargs(self) -> dict:
        """Returns the default values for additional, optional keyword arguments to heatmap plotting methods.
        
        The defaults provide a quick, no-fuss path to plotting the data, and work well and have been tested
        in conjunction to the default pitch dimensions and pitch type arguments to the class constructor.
        The plotting methods use these defaults unless they are overridden in their argument list.
        The default values are read-only, and this method returns their values for inspection.

        Returns:
            A dictionary with these keys:
              'heatmap_kwargs': the dictionary of default keyword arguments to the pitch.heatmap()
                method from the mplsoccer package, which is called by the plotting methods.
              'pitch_kwargs': the dictionary of default keyword arguments to the Pitch() constructor
                from the mplsoccer package, which is called by the plotting methods.
              'grid_kwargs': the dictionary of default keyword arguments to the pitch.grid() method
                from the mplsoccer package, which is called by the plotting methods.    
        """
        return {'heatmap_kwargs': self.__default_heatmap_kwargs,
                'pitch_kwargs': self.__default_pitch_kwargs,
                'grid_kwargs': self.__default_grid_kwargs}

    def parse(self) -> None:
        """Parses the XML document.
        
        Parses the XML document and initializes the attributes with 
        the parsed information.

        Returns:
            None 
        """

        ElementTree.parse(self, self.__tf05_fname)
        
        match_info = self.find('TracabDocument')
        self.__match_id = match_info.get('iMatchId')
        self.__home_team_name = match_info.get('sHomeTeamName')
        self.__home_team_id = match_info.get('iHomeTeamId')
        self.__away_team_name = match_info.get('sAwayTeamName')
        self.__away_team_id = match_info.get('iAwayTeamId')
        self.__match_duration = float(match_info.get('iTotalGameTime'))/60000 #duration in minutes
        self.__arena_name = match_info.get('sArenaName')
        self.__arena_id = match_info.get('iArenaId')
        self.__competion_name = match_info.get('sCompetitionName')
        self.__competition_id = match_info.get('iCompetitionId')
        self.__match_date = match_info.get('dtDate')
        self.__season = match_info.get('sSeason')
        self.__season_id = match_info.get('iSeasonId')
        self.__sport_id = match_info.get('iSportId')
        self.__sport_name = match_info.get('sSportName')


    def summary(self) -> None:
        """Prints a match summary.
        
        Prints a brief summary of the match from the data.
        Additional information can be accessed through the class properties.

        Returns:
            None
        """

        print(f"Source file: {self.tf05_fname}")
        print(f"Home team name and ID:{self.home_team_name}, {self.home_team_id}")
        print(f"Away team name and ID: {self.away_team_name}, {self.away_team_id}")
        print(f"Match date: {self.match_date}")
        print(f"Match ID: {self.match_id}")
        print(f"Match duration: {self.match_duration} minutes")
        
    
    def __make_heatmap_array(self, hm_string: str) -> np.array:
        """Constructs a numpy array from the document's string heatmap."""

        hm_array = (np.array([int(c) for c in hm_string])).reshape(self.__HM_WIDTH,self.__HM_LENGTH)
        return hm_array
                              
    def __plot_core_heatmap(self, hm_array: np.array, pitch_kwargs: dict, hm_kwargs: dict, grid_kwargs: dict) -> dict:
        """Plot the core heatmap."""
        
        if pitch_kwargs is None:
            pitch_kwargs = self.__default_pitch_kwargs
        if hm_kwargs is None:
            hm_kwargs = self.__default_heatmap_kwargs
        if grid_kwargs is None:
            grid_kwargs = self.__default_grid_kwargs
        
        if 'pitch_type' not in pitch_kwargs:
            pitch_kwargs['pitch_type'] = self.pitch_type
        if 'pitch_width' not in pitch_kwargs:
            pitch_kwargs['pitch_width'] = self.pitch_width
        if 'pitch_length' not in pitch_kwargs:
            pitch_kwargs['pitch_length'] = self.pitch_length    
        
        #This comes from an example in the mplsoccer online documentation
        pitch = mpl.Pitch(**pitch_kwargs)
        fig, axs = pitch.grid(**grid_kwargs)
        if 'pitch_color' in pitch_kwargs:
            fig.set_facecolor(pitch_kwargs['pitch_color']) 

        # pitch.heatmap() expects as argument the output produced by pitch.bin_statistic(),
        # however we already have the 'statistic', which is the heatmap array read in from the XML file.
        # All we need from bin_statistic() are the heatmap bucket coordinates. So we use random 
        # data just to produce the bucket edges, but over-write the 'statistic' output with our own data.
        x = np.random.rand(100,) * pitch_kwargs['pitch_length']
        y = np.random.rand(100,) * pitch_kwargs['pitch_width']
        bin_stats = pitch.bin_statistic(x,y, statistic='count', bins=(self.__HM_LENGTH,self.__HM_WIDTH))
        bin_stats['statistic'] = hm_array #forcefully replacing the counts with given heatmap        
        phm = pitch.heatmap(bin_stats, ax = axs['pitch'], **hm_kwargs)
        
        return {'fig': fig, 'axs': axs, 'phm': phm, 'pitch': pitch} #documented in the calling function
    

    def __add_colorbar(self, fig, phm):
        """Adds a colorbar to an existing heatmap."""

        # These work well with defaults; no guarantees for other choices
        ax_cbar = fig.add_axes((0.915, 0.093, 0.03, 0.786))
        cbar = plt.colorbar(phm, cax=ax_cbar)
        cbar.outline.set_edgecolor('#efefef')
        cbar.ax.yaxis.set_tick_params(color='#efefef')
        plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='#efefef')
        

    def __add_endnote(self, ax) -> None:
        """Add the match info as an endonte to the plots."""
        
        endnote_text = '{} v. {}, {}'.format(self.__home_team_name, self.__away_team_name, self.__match_date)
        ax.text(1, 0.5, endnote_text, va='center', ha='right', fontsize=15, color='white')
        
        
    def get_team(self, team: str) -> Element:
        """Returns the team node.
        
        Returns the node in the XML document corresponding to the requested team.

        Args:
            team: either 'home', 'away', or the name of the team (exact spelling).

        Returns:
            An ElementTree.Element object.
        
        Raises:
            A ValueError if the team argument is invalid. 
        """
        
        if team in ['home', 'away']:
            this_team = self.find(self.__team_dict[team])
        elif team == self.__home_team_name:
            this_team = self.find(self.__team_dict['home'])
        elif  team == self.__away_team_name:
            this_team = self.find(self.__team_dict['away'])
        else:
            raise ValueError("Invalid team argument: must be 'home', 'away', or the exact team name. Check your spelling")
        return this_team
    
    def get_team_players(self, team: str) -> dict:
        """Returns all of a team's players.
        
        Args:
            team: either 'home' or 'away' or the name of the team (exact spelling). 

        Returns:
            A dictionary of players:
              'id': the player id
              'jersey': the jersey number of tha player
              'name': the name of the player
        """
        
        this_team = self.get_team(team)
        players = this_team.findall('Player')
        player_id = []
        player_name = []
        player_jersey = []
        for p in players:
            player_id.append(p.get('iPlayerId'))
            player_name.append(p.get('sPlayerName'))
            player_jersey.append(p.get('iJersey'))
        
        return {'id': player_id, 'jersey': player_jersey, 'name': player_name}


    def get_team_possession(self, team: str) -> dict:
        """Returns a team's possession statistics.
        
         Args:
            team: either 'home' or 'away' or the name of the team (exact spelling).

        Returns:
            A dictionary with keys:
              'agv_possession_time': the average duration of a possession sequence, in seconds.
              'pct_possession': the overall percentage of possession.    
        """

        possession_stats = (self.get_team(team)).find('PossessionData')
        avg_possession_time = float(possession_stats.get('iAvgTimePerPossession'))/1000 #ms -> sec
        pct_possession = float(possession_stats.get('fPossessionPercentage'))
        return {'avg_possession_time': avg_possession_time, 'pct_possession': pct_possession}

    
    def team_heatmap(self, team: str, hm_type: str = 'overall', add_cbar: bool = False, pitch_kwargs: dict = None,
                     hm_kwargs: dict = None, grid_kwargs: dict = None) -> dict:
        """Plots a heatmap for a team.
        
        Plots a heatmap for the given team, cumulative over the entire duration of the match.
        Relies on the mplsoccer package to create the pitch object and to plot the heatmap.
        
        Args:
            team: either 'home' or 'away' or the name of the team (exact spelling).
            hm_type: the type of heatmap to plot. Must be one of:
              'overall': the entire team (default).
              'defence': the heatmap generated by the defenders.
              'midfield': the heatmap generated by the midfielders.
              'attack': the heatmap generated by the attackers 
            add_cbar: if True, add a default colorbar to the hetamap (default is False)
            pitch_kwargs: any keyword arguments that can be provided to mplsoccer.Pitch().
              If None, uses the default arguments (default is None).
            hm_kwargs: any keyword arguments that can be provided to pitch.heatmap().
              If None, uses the default arguments (default is None).
            grid_kwargs: any keyword arguments that can be provided to pitch.grid().
              If None, uses the default arguments (default is None).  

        Returns:
            A dictionary of handles to graphics objects for optional further manipulation, with keys:
            'fig': the handle to the figure, as returned by pitch.grid().
            'axs': the set of axes as returned by pitch.grid().
            'phm': the handle to the heatmap, as returned by pitch.heatmap().
            'pitch': the pitch object created by mplsoccer.Pitch().

        Raises:
            A ValueError if the heatmap type is invalid.
        """
        
        this_team = self.get_team(team)
        
        if hm_type not in self.__team_heatmap_dict.keys():
            valid_heatmaps = ", ".join([h for h in self.__team_heatmap_dict.keys()])
            raise ValueError("Invalid heatmap type: must be one of ({}), but provided {}".format(valid_heatmaps, hm_type))
            
        hm_string = this_team.get(self.__team_heatmap_dict[hm_type])
        hm_array = self.__make_heatmap_array(hm_string)      
        hm_params = self.__plot_core_heatmap(hm_array, pitch_kwargs, hm_kwargs, grid_kwargs)
        
        # Add title
        if team == 'home':
            this_team_name = self.__home_team_name
        elif team == 'away':
            this_team_name = self.__away_team_name
        else:
            this_team_name = team
        title_text ='{} - {}'.format(this_team_name, hm_type)
        axs = hm_params['axs']
        _ = axs['title'].text(0.5, 0.45, title_text, color='white',
                             va='center', ha='center', fontsize=30) #path_effects=path_eff,
                             #fontproperties=robotto_regular.prop, fontsize=30)
        
        # Put the match info in the end note
        self.__add_endnote(axs['endnote'])
          
        # Optional: add cbar?
        if add_cbar:
            self.__add_colorbar(hm_params['fig'], hm_params['phm'])
            
        return hm_params


    def team_possession_heatmap(self, team: str, possession: str = 'in', hm_type: str = 'overall', add_cbar: bool = False,
                                pitch_kwargs: dict = None, hm_kwargs: dict = None, grid_kwargs: dict = None) -> dict:
        """Plots a possession heatmap for a team.
        
        Plots a possession heatmap for the given team: can be in-possession or out-of-possession,
        for the entire match, or for one of the two halves. For example, one can visalize the
        heatmap of a team while the team is in possession during the first half. 
        Relies on the mplsoccer package to create the pitch object and to plot the heatmap.
        
        Args:
            team: either 'home' or 'away' or the name of the team (exact spelling).
            possession: either 'in' or 'out' for in-possession and out-of-possession. (default is 'in')
            hm_type: the type of heatmap to plot. Must be one of:
              'overall': the entire match (default).
              'first-half': only the first half.
              'second-half': only the second half. 
            add_cbar: if True, add a default colorbar to the hetamap (default is False)
            pitch_kwargs: any keyword arguments that can be provided to mplsoccer.Pitch().
              If None, uses the default arguments (default is None).
            hm_kwargs: any keyword arguments that can be provided to pitch.heatmap().
              If None, uses the default arguments (default is None).
            grid_kwargs: any keyword arguments that can be provided to pitch.grid().
              If None, uses the default arguments (default is None).

        Returns:
            A dictionary of handles to graphics objects for optional further manipulation, with keys:
            'fig': the handle to the figure, as returned by pitch.grid().
            'axs': the set of axes as returned by pitch.grid().
            'phm': the handle to the heatmap, as returned by pitch.heatmap().
            'pitch': the pitch object created by mplsoccer.Pitch().

        Raises:
            A ValueError if the heatmap type or possession type is invalid.
        """
        
        # Get the team - also checks valid team string
        this_team = self.get_team(team)
        
        summary_possession_stats = this_team.find('PossessionData')
        if possession == 'in':
            possession_data = summary_possession_stats.find('OwnTeamPossession')
        elif possession == 'out':
            possession_data = summary_possession_stats.find('OpponentPossession')
        else:
            raise ValueError("Inavlid possession type: must be one of ('in', 'out'), but provided {}".format(possession))
        
        if hm_type not in self.__possession_heatmap_dict.keys():
            valid_heatmaps = ", ".join([h for h in self.__possession_heatmap_dict.keys()])
            raise ValueError("Invalid heatmap type: must be one of ({}), but provided {}".format(valid_heatmaps, hm_type)) 
        hm_string = possession_data.get(self.__possession_heatmap_dict[hm_type])
        hm_array = self.__make_heatmap_array(hm_string)
        hm_params = self.__plot_core_heatmap(hm_array, pitch_kwargs, hm_kwargs, grid_kwargs)
            
         # BEGIN Add title
        if team == 'home':
            this_team_name = self.__home_team_name
        elif team == 'away':
            this_team_name = self.__away_team_name
        else:
            this_team_name = team
        if possession == 'in':
            possession_string = 'in possession'
        elif possession == 'out':
            possession_string = 'out of possession'
        else: # this should never happen because we checked up above - keeping it in case code changes
            raise ValueError("Inavlid possession type: must be one of ('in', 'out'), but provided {}".format(possession))
                
        title_text = f'{this_team_name} - {possession_string} - {hm_type}'
        axs = hm_params['axs']
        _ = axs['title'].text(0.5, 0.75, title_text, color='white',
                             va='center', ha='center', fontsize=30)
        # Add possession time and percentage only to the overall heatmap because the data only provide overall numbers.
        # It would be confusing to add them to first-half and second-half heatmaps
        if hm_type == 'overall': 
            possession_stats = self.get_team_possession(team)
            # Note y coordinate: placement is below the previous title, and the font is smaller so this results in a sub-title
            _ = axs['title'].text(0.5, 0.05, 
                                  f"Possession: {possession_stats['pct_possession']:.0f}% Avg. time/possession:{possession_stats['avg_possession_time']: 1.1f}s",
                                  color='white', va='center', ha='center', fontsize=15)
        # END Add title
        
        # Put the match info in the endnote
        self.__add_endnote(axs['endnote'])
    
        if add_cbar:
            self.__add_colorbar(hm_params['fig'], hm_params['phm'])
            
        return hm_params
    
    
    def get_player(self, player: Union[str, int]) -> Tuple[Element, str]:
        """Finds a player."""
        
        #Find the player
        player = str(player)
        home_team = self.find('HomeTeam')
        away_team = self.find('AwayTeam') 
        
        # Try searching by player id first
        query_by_id = "Player/[@iPlayerId='{}']".format(player)
        player_node = home_team.find(query_by_id)
        player_team = home_team.get('sTeamName')

        if player_node is None: # we did not find the player within the home team
            player_node = away_team.find(query_by_id)
            player_team = away_team.get('sTeamName')
                
        # If still no result, try searching by name
        if player_node is None:
            query_by_name = "Player/[@sPlayerName='{}']".format(player)         
            player_node = home_team.find(query_by_name)
            player_team = home_team.get('sTeamName')
            if player_node is None:
                player_node = away_team.find(query_by_name)
                player_team = away_team.get('sTamName')
            
        # If still not found, something's wrong
        if player_node is None:
            player_team = None
            raise ValueError("Player node not found. Check the player ID or player name you provided. Player names must be spelled exactly as they are in the document.")
        
        return (player_node, player_team)
    
    
    def player_heatmap(self, player: Union[str,int], add_cbar: bool = False, pitch_kwargs: dict = None, 
                       hm_kwargs: dict = None, grid_kwargs: dict = None) -> dict:
        """Plots the overall, whole-game heatmap and average location of a player. 
        
        Args:
          player: the player ID or the player name (exact match).
          add_cbar: if True, add a default colorbar to the hetamap (default is False)
          pitch_kwargs: any keyword arguments that can be provided to mplsoccer.Pitch().
              If None, uses the default arguments (default is None).
          hm_kwargs: any keyword arguments that can be provided to pitch.heatmap().
              If None, uses the default arguments (default is None).
          grid_kwargs: any keyword arguments that can be provided to pitch.grid().
              If None, uses the default arguments (default is None).

        Returns:
            A dictionary of handles to graphics objects for optional further manipulation, with keys:
            'fig': the handle to the figure, as returned by pitch.grid().
            'axs': the set of axes as returned by pitch.grid().
            'phm': the handle to the heatmap, as returned by pitch.heatmap().
            'pitch': the pitch object created by mplsoccer.Pitch().

        Raises:
            A ValueError if the player is not found.
        """
        
        (this_player, player_team) = self.get_player(player)
        # Frustrating: coordinates are always in some other frame of reference!
        # Found out by trial and error that we must flip these
        avg_x = -1.0 * float(this_player.get('fAvgPosX'))
        avg_y = -1.0 * float(this_player.get('fAvgPosY'))
        hm_string = this_player.get('sHeatmap')
        hm_array = self.__make_heatmap_array(hm_string)
        hm_params = self.__plot_core_heatmap(hm_array, pitch_kwargs, hm_kwargs, grid_kwargs)
        axs = hm_params['axs']
        pitch = hm_params['pitch']
        pitch.scatter(avg_x, avg_y, s=100, c='red', marker='o', ax=axs['pitch'])
        
        # Add title
        player_name = this_player.get('sPlayerName')
        player_jersey = this_player.get('iJersey')
        title_text = f'{player_name} - {player_team} #{player_jersey} - overall'
        _ = axs['title'].text(0.5, 0.75, title_text, color='white',
                             va='center', ha='center', fontsize=30)
        # Add endnote
        self.__add_endnote(axs['endnote'])
        
        if add_cbar:
            self.__add_colorbar(hm_params['fig'], hm_params['phm'])

        return hm_params

    def player_possession_heatmap(self, player: Union[str,int], possession: str = 'in', hm_type: str = 'overall',
                                  add_cbar: bool = False, pitch_kwargs: dict = None, hm_kwargs: dict = None,
                                  grid_kwargs: dict = None) -> dict:
        """Plots a possession heatmap for a player.
        
        Plots a possession heatmap for a player: can be in-possession or out-of-possession,
        for the entire match, or for one of the two halves. For example, one can visalize the
        heatmap of a player while that player's team is in possession during the first half. 
        Relies on the mplsoccer package to create the pitch object and to plot the heatmap.

        Examples:
          # De Bruyne's heatmap while his team is in possession, for the entire match.
          source.player_possession_heatmap('Kevin DE BRUYNE', possession='in')

          # Megan Rapinoe's heatmap while her team is out of possession, in the second half.
          source.player_possession_heatmap('Megan RAPINOE', possession='out', hm_type='second-half')

          # Player ID 123456, overall heatmap while in possession
          source.player_possession_heatmap(123456)
        
        Args:
            player: either 'home' or 'away' or the name of the team (exact spelling).
            possession: either 'in' or 'out' for in-possession and out-of-possession. (default is 'in')
            hm_type: the type of heatmap to plot. Must be one of:
              'overall': the entire match (default).
              'first-half': only the first half.
              'second-half': only the second half. 
            add_cbar: if True, add a default colorbar to the hetamap (default is False)
            pitch_kwargs: any keyword arguments that can be provided to mplsoccer.Pitch().
              If None, uses the default arguments (default is None).
            hm_kwargs: any keyword arguments that can be provided to pitch.heatmap().
              If None, uses the default arguments (default is None).
            grid_kwargs: any keyword arguments that can be provided to pitch.grid().
              If None, uses the default arguments (default is None).  

        Returns:
            A dictionary of handles to graphics objects for optional further manipulation, with keys:
            'fig': the handle to the figure, as returned by pitch.grid().
            'axs': the set of axes as returned by pitch.grid().
            'phm': the handle to the heatmap, as returned by pitch.heatmap().
            'pitch': the pitch object created by mplsoccer.Pitch().

        Raises:
            A ValueError if the player is not found or the possession type or heatmap type is invalid.
        """
        

         # Get the player - also checks valid team string
        (this_player, player_team) = self.get_player(player)
        
        summary_possession_stats = this_player.find('PossessionData')
        if possession == 'in':
            possession_data = summary_possession_stats.find('OwnTeamPossession')
        elif possession == 'out':
            possession_data = summary_possession_stats.find('OpponentPossession')
        else:
            raise ValueError("Inavlid possession type: must be one of ('in', 'out'), but provided {}".format(possession))
        
        if hm_type not in self.__possession_heatmap_dict.keys():
            valid_heatmaps = ", ".join([h for h in self.__possession_heatmap_dict.keys()])
            raise ValueError("Invalid heatmap type: must be one of ({}), but provided {}".format(valid_heatmaps, hm_type)) 
        hm_string = possession_data.get(self.__possession_heatmap_dict[hm_type])
        hm_array = self.__make_heatmap_array(hm_string)
        hm_params = self.__plot_core_heatmap(hm_array, pitch_kwargs, hm_kwargs, grid_kwargs) 
        
        # BEGIN Add title
        if possession == 'in':
            possession_string = 'in possession'
        elif possession == 'out':
            possession_string = 'out of possession'
        else: # this "else" branch should never happen because we checked up above - keeping it in case code changes
            raise ValueError("Inavlid possession type: must be one of ('in', 'out'), but provided {}".format(possession))
            
        player_name = this_player.get('sPlayerName')
        player_jersey = this_player.get('iJersey')
        title_text = f'{player_name} - {player_team} #{player_jersey} - {possession_string} - {hm_type}'
        axs = hm_params['axs']
        _ = axs['title'].text(0.5, 0.75, title_text, color='white',
                             va='center', ha='center', fontsize=30)
        # END Add title
        
        # Add match info at the bottom
        self.__add_endnote(axs['endnote'])
        
        # Add colorbar?
        if add_cbar:
            self.__add_colorbar(hm_params['fig'], hm_params['phm'])

        return hm_params