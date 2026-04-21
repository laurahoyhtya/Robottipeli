import pygame
import random

leveys = 640
korkeus = 480
fps = 60

robon_nopeus = 6
hirvion_nopeus = 1.5
kolikoiden_maara = 8

valkoinen = (255, 255, 255)
musta = (0, 0, 0)
tummansininen = (20, 30, 60)
vihrea = (50, 180, 90)
punainen = (220, 70, 70)
keltainen = (250, 220, 80)

class Peliolio:
    def __init__(self, kuva, x, y):
        self.kuva = kuva
        # Luodaan Rect-olio, jotta olion sijainnin käsittely olisi helpompaa.
        # Tämän ansiosta esim. self.sijainti.x antaa jatkossa olion vasemman yläkulman x-koordinaatin jne.  
        self.sijainti = self.kuva.get_rect(topleft=(x, y))
    
    def piirra(self, ikkuna):
        ikkuna.blit(self.kuva, self.sijainti)

class Robo(Peliolio):
    def __init__(self, kuva, x, y):
        super().__init__(kuva, x, y)
        self.nopeus = robon_nopeus
    
    def liiku(self, napit):
        if napit[pygame.K_LEFT]:
            self.sijainti.x -= self.nopeus
        if napit[pygame.K_RIGHT]:
            self.sijainti.x += self.nopeus
        if napit[pygame.K_UP]:
            self.sijainti.y -= self.nopeus
        if napit[pygame.K_DOWN]:
            self.sijainti.y += self.nopeus
        
        if self.sijainti.left < 0:
            self.sijainti.left = 0
        if self.sijainti.right > leveys:
            self.sijainti.right = leveys
        if self.sijainti.top < 0:
            self.sijainti.top = 0
        if self.sijainti.bottom > korkeus:
            self.sijainti.bottom = korkeus


class Kolikko(Peliolio):
    def __init__(self, kuva, x, y):
        super().__init__(kuva, x, y)
        self.keratty = False
    
# Kolikko ei voi hyödyntää yläluokan piirra-metodia, koska kolikon on kadottava näkyvistä, kun se kerätty. Luodaan siis oma metodi.
    def piirra(self, ikkuna):
        if not self.keratty:
            ikkuna.blit(self.kuva, self.sijainti)
    

class Hirvio(Peliolio):
    def __init__(self, kuva, x, y, nopeus_x, nopeus_y):
        super().__init__(kuva, x, y)
        self.nopeus_x = nopeus_x
        self.nopeus_y = nopeus_y
    
    def liiku(self):
        self.sijainti.x += self.nopeus_x
        self.sijainti.y += self.nopeus_y

        if self.sijainti.left <= 0 or self.sijainti.right >= leveys:
            self.nopeus_x *= -1
        if self.sijainti.top <= 0 or self.sijainti.bottom >= korkeus:
            self.nopeus_y *= -1


class Ovi(Peliolio):
    def __init__(self, kuva, x, y):
        super().__init__(kuva, x, y)


def lataa_kuvat():
    robon_kuva = pygame.image.load("robo.png")
    kolikon_kuva = pygame.image.load("kolikko.png")
    hirvion_kuva = pygame.image.load("hirvio.png")
    oven_kuva = pygame.image.load("ovi.png")
    return robon_kuva, kolikon_kuva, hirvion_kuva, oven_kuva

def luo_kolikot(kolikon_kuva, robon_sijainti, oven_sijainti):
    kolikot = []
    while len(kolikot) < kolikoiden_maara:
        x = random.randint(40, leveys - kolikon_kuva.get_width() - 40)
        y = random.randint(40, korkeus - kolikon_kuva.get_height() - 40)
        uusi_kolikko = Kolikko(kolikon_kuva, x, y)

        # Tarkistetaan, osuvatko kaksi Rect-oliota toisiinsa.
        # Suurennetaan robon ja oven alueita väliaikaisesti, jotta nähdään, ovatko oliot liian lähekkäin.
        liian_lahella_roboa = uusi_kolikko.sijainti.colliderect(robon_sijainti.inflate(100, 100))
        liian_lahella_ovea = uusi_kolikko.sijainti.colliderect(oven_sijainti.inflate(100, 100))

        osuu_toiseen_kolikkoon = False
        for kolikko in kolikot:
            if uusi_kolikko.sijainti.colliderect(kolikko.sijainti.inflate(30, 30)):
                osuu_toiseen_kolikkoon = True
        
        if not liian_lahella_roboa and not liian_lahella_ovea and not osuu_toiseen_kolikkoon:
            kolikot.append(uusi_kolikko)

    return kolikot

def luo_hirviot(hirvion_kuva):
    hirviot = []
    hirviot.append(Hirvio(hirvion_kuva, 120, 100, hirvion_nopeus, 0))
    hirviot.append(Hirvio(hirvion_kuva, 380, 150, 0, hirvion_nopeus))
    hirviot.append(Hirvio(hirvion_kuva, 250, 320, hirvion_nopeus, hirvion_nopeus))
    hirviot.append(Hirvio(hirvion_kuva, 50, 50, hirvion_nopeus, 0))
    hirviot.append(Hirvio(hirvion_kuva, 500, 300, 0, hirvion_nopeus))
    
    return hirviot
    
def kasittele_kolikko_osumat(robo, kolikot):
    keratyt_talla_kierroksella = 0

    for kolikko in kolikot:
        if not kolikko.keratty and robo.sijainti.colliderect(kolikko.sijainti):
            kolikko.keratty = True
            keratyt_talla_kierroksella += 1
        
    return keratyt_talla_kierroksella
    
def osuuko_hirvio_roboon(robo, hirviot):
    for hirvio in hirviot:
        if robo.sijainti.colliderect(hirvio.sijainti):
            return True
    return False
    
def kaikki_kolikot_keratty(kolikot):
    for kolikko in kolikot:
        if not kolikko.keratty:
            return False
    return True

def osuuko_robo_oveen(robo, ovi):
    return robo.sijainti.colliderect(ovi.sijainti)

def piirra_laskuri(ikkuna, fontti, keratyt_kolikot, kolikoita_yhteensa, tavoite_valmis):
    kolikkoteksti = fontti.render(f"Kolikot: {keratyt_kolikot}/{kolikoita_yhteensa}", True, valkoinen)
    ikkuna.blit(kolikkoteksti, (20, 20))

    if tavoite_valmis:
        tavoiteteksti = fontti.render("Tavoite valmis, mene ovelle!", True, keltainen)
    else:
        tavoiteteksti = fontti.render("Kerää kaikki kolikot", True, valkoinen)
    ikkuna.blit(tavoiteteksti, (20, 50))

def piirra_peli(ikkuna, robo, kolikot, hirviot, ovi, fontti, keratyt_kolikot, kolikoita_yhteensa):
    ikkuna.fill(tummansininen)

    ovi.piirra(ikkuna)

    for kolikko in kolikot:
        kolikko.piirra(ikkuna)
    
    for hirvio in hirviot:
        hirvio.piirra(ikkuna)
    
    robo.piirra(ikkuna)

    piirra_laskuri(ikkuna, fontti, keratyt_kolikot, kolikoita_yhteensa, keratyt_kolikot == kolikoita_yhteensa)

    pygame.display.flip()

def nayta_lopetusruutu(ikkuna, iso_fontti, pieni_fontti, voitto, keratyt_kolikot, kolikoita_yhteensa):
    ikkuna.fill(musta)
    
    if voitto:
        otsikko = iso_fontti.render("Voitit pelin!", True, vihrea)
        teksti = pieni_fontti.render("Keräsit kaikki kolikot ja pääsit ovelle", True, valkoinen)
    else:
        otsikko = iso_fontti.render("Hävisit pelin!", True, punainen)
        teksti = pieni_fontti.render("Hirviö osui roboon", True, valkoinen)

    tulosteksti = pieni_fontti.render(f"Kolikot: {keratyt_kolikot}/{kolikoita_yhteensa}", True, valkoinen)
    lopetusteksti = pieni_fontti.render("Sulje ikkuna lopettaaksesi", True, valkoinen)

    ikkuna.blit(otsikko, (leveys // 2 - otsikko.get_width() // 2, 150))
    ikkuna.blit(teksti, (leveys // 2 - teksti.get_width() // 2, 220))
    ikkuna.blit(tulosteksti, (leveys // 2 - tulosteksti.get_width() // 2, 260))
    ikkuna.blit(lopetusteksti, (leveys // 2 - lopetusteksti.get_width() // 2, 320))

    pygame.display.flip()

def paaohjelma():
    pygame.init()
    ikkuna = pygame.display.set_mode((leveys, korkeus))
    pygame.display.set_caption("Robo ja kolikot")
    kello = pygame.time.Clock()

    fontti = pygame.font.SysFont(None, 30)
    iso_fontti = pygame.font.SysFont(None, 52)
    pieni_fontti = pygame.font.SysFont(None, 32)

    robon_kuva, kolikon_kuva, hirvion_kuva, oven_kuva = lataa_kuvat()

    robo = Robo(robon_kuva, 30, korkeus - robon_kuva.get_height() - 30)
    ovi = Ovi(oven_kuva, leveys - oven_kuva.get_width() - 30, 30)
    kolikot = luo_kolikot(kolikon_kuva, robo.sijainti, ovi.sijainti)
    hirviot = luo_hirviot(hirvion_kuva)

    keratyt_kolikot = 0
    peli_loppui = False
    peli_voitettiin = False
    peli_kaynnissa = True

    while peli_kaynnissa:
        kello.tick(fps)
        for tapahtuma in pygame.event.get():
            if tapahtuma.type == pygame.QUIT:
                peli_kaynnissa = False
        
        if not peli_loppui:
            napit = pygame.key.get_pressed()
            robo.liiku(napit)

            for hirvio in hirviot:
                hirvio.liiku()
            
            keratyt_kolikot += kasittele_kolikko_osumat(robo, kolikot)

            if osuuko_hirvio_roboon(robo, hirviot):
                peli_loppui = True
                peli_voitettiin = False
            
            elif kaikki_kolikot_keratty(kolikot) and osuuko_robo_oveen(robo, ovi):
                peli_loppui = True
                peli_voitettiin = True
            
            piirra_peli(ikkuna, robo, kolikot, hirviot, ovi, fontti, keratyt_kolikot, kolikoiden_maara)

        else:
            nayta_lopetusruutu(ikkuna, iso_fontti, pieni_fontti, peli_voitettiin, keratyt_kolikot, kolikoiden_maara)
        
    pygame.quit()

if __name__ == "__main__":
    paaohjelma()