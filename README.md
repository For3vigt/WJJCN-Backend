This is a project I worked on, together with 4 other students in Fontys hbo-ICT Semester 3.

Original readme below this line.
---

# Documentatie linkscraper
## Beschrijving
De applicatie wordt gestart via een cmd terminal, vervolgens wordt er een link aangegeven aan de scraper. De scraper
vraagt de link op via het internet, vervolgens stript de scraper alle link tags (anchor tags) met de reference 
(href attribuut) van de pagina af. Waarna dit gedaan is wordt de link met de opgegeven start link vergeleken. Bevat de 
link die gevonden is hetzelfde als de start link, dan wordt de link opgeslagen in een lijstje met alle links die 
gevonden zijn.

## Hoe werkt het
Als je een cmd terminal geopend hebt op de locatie waar het main.py script staat, start je het programma door in de 
terminal te typen: 

	python3 main.py

Als het programma helemaal is opgestart, komt er een tekst te staan die vraagt naar welke link er gescraped moet 
worden. Geef vervolgens de link door deze in de terminal in te typen, zie voorbeeld hieronder:

> -- Enter the URL you want to crawl --  
> *https://www.ah.nl/producten*

De scraper gaat vervolgens automatisch alle links ophalen en opslaan die beginnen met de ingegeven link bijv:

> gegeven link: https://www.ah.nl/producten  
> link 1: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;https://www.ah.nl &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(wordt niet opgeslagen)  
> link 2: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;https://www.ah.nl/porducten/coca-cola &nbsp;(wordt wel opgeslagen)

Wanneer de scraper alle links heeft gevonden en ook alle links heeft bezocht, worden deze opgeslagen in een .txt bestand
zodat deze eenvoudig opgehaald kunnen worden.

## Wat moet er zijn geïnstalleerd
Om dit programma te laten werken moet python 3.10 op de pc zijn geïnstalleerd, zorg ervoor dat er geen ander versies van
