HELTROSH_DISCORD_ID = 164698420777320448
KAPER_DISCORD_ID = 687276408057233658

#ERRORS
ADMIN_ONLY_ERROR = "Mě může používat jenom KapEr, co to zkoušíš!"
WRONG_ROUND_OR_LEAGUE = "Špatně zadané kolo/liga. Kolo musí být celé číslo v intervalu 1-9 a liga musí být celé číslo v intervalu 1-6."

#PING DMs
EXCUSED_PING_DM = """Ahoj {discordName},
píšeme ti, lebo nám chýba výsledok tvojho ligového zápasu:
KOLO: {round}.
PROTIVNÍK: {opponent}, {opponentDiscord}

Tvoj zápas sa v tomto týždni nedá odohrať.
Tvoj protivník bol pridaný na listinu dočasne ospravedlnených hráčov -
<#886902603479412736>.

Medzičasom môžeš toto kolo preskočiť a hrať niektoré iné. Aktuálne kolo sa dohrá keď protivník bude znovu k dispozícií."""

NORMAL_PING_DM = """Ahoj {discordName}, 
píšeme ti, lebo nám chýba výsledok tvojho ligového zápasu:
    
KOLO: {round}.
PROTIVNÍK: {opponent}, {opponentDiscord}
DEADLINE: {deadline}

Po odohratí zápasu musí byť jeho výsledok nahlásený najneskôr do dátumu deadlinu.
Zápasy s nenahlásenými výsledkami sú automaticky kontumované Adminom.
**V prípade ak zápas nie je možné odohrať načas, kontaktuj Admina Ligy [KapEr#1695] so žiadosťou o predĺženie deadlinu.**
    
VÝSLEDOK SA NAHLASUJE NA DVOCH MIESTACH:
1) AOEliga Discord Server
<#{discordChannel}>
2) **Challonge Bracket**
<{bracketURL}>"""