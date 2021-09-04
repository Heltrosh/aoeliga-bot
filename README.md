# AoELigaBot Documentation

## Commands

#### !help
Syntax: !help OR !help \<command\>

Shows either the default help message or a syntax of the specified command.

#### !pinground
Syntax: !pinground \<round\> \<league\>

Sends a DM to everyone inside a league, who didn't submit a result for that specific round. Semifinals are coded as round 8 and finals as round 9.

#### !excuse
Syntax: !excuse list OR !excuse \<challongename\> OR !excuse \<challongename\> \<round(s)\>
        
First version of the command lists all players, who are excused from any round along with the rounds they are excused from.

Second version of the command checks if a given player is excused from any rounds and responds accordingly (says so if no, lists rounds if yes)

Third version of the command excuses a player from given round(s) if he isn't yet excused from those and vice versa. Accepts multiple rounds, e.g. !excuse Heltrosh 1 4 8 

For names with a space in it, you have to use quotation marks (!excuse "Helt rosh")

#### !load 
Syntax: !load \<extension\>

Loads an extension(cog) - e.g. !load dmall

#### !unload
Syntax: !unload \<extension\>

Unloads an extension(cog) - e.g. !unload dmall

#### !dmall
Syntax: !dmall \<message\>

Sends a DM to everyone in the discord server. HAS to be loaded through the !load command

