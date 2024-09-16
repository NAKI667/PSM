import sqlite3  
import random  
import string  
import tkinter as tk  
from tkinter import messagebox, simpledialog, ttk  
from cryptography.fernet import Fernet  

class Veritabani:
    def __init__(self, db_adi="sifre_yoneticisi.db"):
        self.baglanti = sqlite3.connect(db_adi)  
        self.imlec = self.baglanti.cursor()  
        self.tablolari_olustur()  
        self.anahtar = self.anahtar_yukle()  

    def tablolari_olustur(self):
        self.imlec.execute("""
            CREATE TABLE IF NOT EXISTS kullanicilar (
                kullanici_adi TEXT PRIMARY KEY,
                sifre TEXT NOT NULL
            )
        """)
        self.imlec.execute("""
            CREATE TABLE IF NOT EXISTS sifreler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kullanici_adi TEXT,
                web_sitesi TEXT,
                kullanici_adi_sifre TEXT,
                sifre TEXT,
                FOREIGN KEY(kullanici_adi) REFERENCES kullanicilar(kullanici_adi)
            )
        """)
        self.baglanti.commit()  

    def anahtar_yukle(self):
        try:
            with open("gizli.anahtar", "rb") as anahtar_dosyasi:
                return anahtar_dosyasi.read()
        except FileNotFoundError:
            anahtar = Fernet.generate_key()
            with open("gizli.anahtar", "wb") as anahtar_dosyasi:
                anahtar_dosyasi.write(anahtar)
            return anahtar

    def sifrele(self, veri):
        fernet = Fernet(self.anahtar)
        return fernet.encrypt(veri.encode()).decode()

    def desifrele(self, veri):
        fernet = Fernet(self.anahtar)
        return fernet.decrypt(veri.encode()).decode()

    def kullanici_ekle(self, kullanici_adi, sifre):
        try:
            sifrelenmis_sifre = self.sifrele(sifre)
            self.imlec.execute("INSERT INTO kullanicilar (kullanici_adi, sifre) VALUES (?, ?)", (kullanici_adi, sifrelenmis_sifre))
            self.baglanti.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def kullanici_kontrol(self, kullanici_adi, sifre):
        self.imlec.execute("SELECT sifre FROM kullanicilar WHERE kullanici_adi = ?", (kullanici_adi,))
        sonuc = self.imlec.fetchone()
        if sonuc and self.desifrele(sonuc[0]) == sifre:
            return True
        return False

    def sifre_ekle(self, kullanici_adi, web_sitesi, kullanici_adi_sifre, sifre):
        sifrelenmis_sifre = self.sifrele(sifre)
        self.imlec.execute("INSERT INTO sifreler (kullanici_adi, web_sitesi, kullanici_adi_sifre, sifre) VALUES (?, ?, ?, ?)",
                            (kullanici_adi, web_sitesi, kullanici_adi_sifre, sifrelenmis_sifre))
        self.baglanti.commit()

    def sifreleri_al(self, kullanici_adi):
        self.imlec.execute("SELECT web_sitesi, kullanici_adi_sifre, sifre FROM sifreler WHERE kullanici_adi = ?", (kullanici_adi,))
        sonuclar = self.imlec.fetchall()
        desifrelenmis_sonuclar = [(web_sitesi, kullanici_adi_sifre, self.desifrele(sifre)) for web_sitesi, kullanici_adi_sifre, sifre in sonuclar]
        return desifrelenmis_sonuclar


class SifreYoneticisiUygulamasi:
    def __init__(self, ana_ekran):
        self.ana_ekran = ana_ekran  
        self.ana_ekran.title("Parola Yöneticisi")  
        self.ana_ekran.geometry("500x400")  

        self.veritabani = Veritabani()  

        self.ana_cerceve = tk.Frame(ana_ekran)  
        self.ana_cerceve.pack(pady=20)  

        self.etiket = tk.Label(self.ana_cerceve, text="Bir seçenek seçin:")  
        self.etiket.pack(pady=10)  

        self.giris_butonu = tk.Button(self.ana_cerceve, text="Giriş", command=self.giris, width=30)
        self.giris_butonu.pack(pady=5)

        self.kayit_butonu = tk.Button(self.ana_cerceve, text="Kayıt Ol", command=self.kayit_ol, width=30)
        self.kayit_butonu.pack(pady=5)

        self.sifre_uret_butonu = tk.Button(self.ana_cerceve, text="Parola Üret", command=self.sifre_uret, width=30)
        self.sifre_uret_butonu.pack(pady=5)

    def cerceve_temizle(self):
        for widget in self.ana_cerceve.winfo_children():
            widget.destroy()

    def giris(self):
        self.cerceve_temizle()
        self.ana_cerceve.pack(pady=20)

        self.kullanici_adi_etiketi = tk.Label(self.ana_cerceve, text="Kullanıcı Adı:")
        self.kullanici_adi_etiketi.pack()

        self.kullanici_adi_giris = tk.Entry(self.ana_cerceve)
        self.kullanici_adi_giris.pack()

        self.sifre_etiketi = tk.Label(self.ana_cerceve, text="Parola:")
        self.sifre_etiketi.pack()

        self.sifre_giris = tk.Entry(self.ana_cerceve, show="*")
        self.sifre_giris.pack()

        self.giris_butonu = tk.Button(self.ana_cerceve, text="Giriş", command=self.girisi_kontrol)
        self.giris_butonu.pack(pady=5)

        self.geri_butonu = tk.Button(self.ana_cerceve, text="Geri", command=self.ana_menuyu_goster)
        self.geri_butonu.pack(pady=5)

    def girisi_kontrol(self):
        kullanici_adi = self.kullanici_adi_giris.get()
        sifre = self.sifre_giris.get()
        if self.veritabani.kullanici_kontrol(kullanici_adi, sifre):
            messagebox.showinfo("Bilgi", "Giriş başarılı")
            self.kullanici_arayuzunu_goster(kullanici_adi)
        else:
            messagebox.showerror("Hata", "Geçersiz kullanıcı adı veya parola")

    def kayit_ol(self):
        self.cerceve_temizle()
        self.ana_cerceve.pack(pady=20)

        self.kullanici_adi_etiketi = tk.Label(self.ana_cerceve, text="Kullanıcı Adı:")
        self.kullanici_adi_etiketi.pack()

        self.kullanici_adi_giris = tk.Entry(self.ana_cerceve)
        self.kullanici_adi_giris.pack()

        self.sifre_etiketi = tk.Label(self.ana_cerceve, text="parola:")
        self.sifre_etiketi.pack()

        self.sifre_giris = tk.Entry(self.ana_cerceve, show="*")
        self.sifre_giris.pack()

        self.kayit_butonu = tk.Button(self.ana_cerceve, text="Kayıt Ol", command=self.kullanici_kaydet)
        self.kayit_butonu.pack(pady=5)

        self.geri_butonu = tk.Button(self.ana_cerceve, text="Geri", command=self.ana_menuyu_goster)
        self.geri_butonu.pack(pady=5)

    def kullanici_kaydet(self):
        kullanici_adi = self.kullanici_adi_giris.get()
        sifre = self.sifre_giris.get()

        if kullanici_adi.strip() == "" or sifre.strip() == "":
            messagebox.showerror("Hata", "Kullanıcı adı ve parola alanları boş bırakılamaz")
            return

        if self.veritabani.kullanici_ekle(kullanici_adi, sifre):
            messagebox.showinfo("Bilgi", "Kayıt başarılı")
            self.ana_menuyu_goster()
        else:
            messagebox.showerror("Hata", "Kullanıcı adı zaten mevcut")

    def guclu_sifre_uret(self, uzunluk=12):
        karakter_seti = string.ascii_letters + string.digits + string.punctuation
        sifre = ''.join(random.choice(karakter_seti) for _ in range(uzunluk))
        return sifre

    def sifre_uret(self):
        self.cerceve_temizle()
        self.ana_cerceve.pack(pady=20)

        self.sifre_etiketi = tk.Label(self.ana_cerceve, text="Parola Uzunluğu:")
        self.sifre_etiketi.pack()

        self.sifre_uzunluk_giris = tk.Entry(self.ana_cerceve)
        self.sifre_uzunluk_giris.pack()

        self.sifre_uret_butonu = tk.Button(self.ana_cerceve, text="Parola Üret", command=self.sifre_uret_goster)
        self.sifre_uret_butonu.pack(pady=5)

        self.geri_butonu = tk.Button(self.ana_cerceve, text="Geri", command=self.ana_menuyu_goster)
        self.geri_butonu.pack(pady=5)

    def sifre_uret_goster(self):
        try:
            uzunluk = int(self.sifre_uzunluk_giris.get())
            sifre = self.guclu_sifre_uret(uzunluk)
            self.cerceve_temizle()
            self.ana_cerceve.pack(pady=20)

            self.sifre_etiketi = tk.Label(self.ana_cerceve, text="Üretilen Parola:")
            self.sifre_etiketi.pack()

            sifre_giris = tk.Entry(self.ana_cerceve, width=40)
            sifre_giris.insert(0, sifre)
            sifre_giris.config(state='readonly')
            sifre_giris.pack()

            kopyala_butonu = tk.Button(self.ana_cerceve, text="Panoya Kopyala", command=lambda: self.pano_ya_kopyala(sifre))
            kopyala_butonu.pack(pady=5)

            self.geri_butonu = tk.Button(self.ana_cerceve, text="Geri", command=self.ana_menuyu_goster)
            self.geri_butonu.pack(pady=5)
        except ValueError:
            messagebox.showerror("Hata", "Geçersiz parola uzunluğu")


    def pano_ya_kopyala(self, metin):
        self.ana_ekran.clipboard_clear()
        self.ana_ekran.clipboard_append(metin)
        messagebox.showinfo("Bilgi", "Metin panoya kopyalandı")

    def ana_menuyu_goster(self):
        self.cerceve_temizle()
        self.ana_cerceve.pack(pady=20)

        self.etiket = tk.Label(self.ana_cerceve, text="Bir seçenek seçin:")
        self.etiket.pack(pady=10)

        self.giris_butonu = tk.Button(self.ana_cerceve, text="Giriş", command=self.giris, width=30)
        self.giris_butonu.pack(pady=5)

        self.kayit_butonu = tk.Button(self.ana_cerceve, text="Kayıt Ol", command=self.kayit_ol, width=30)
        self.kayit_butonu.pack(pady=5)

        self.sifre_uret_butonu = tk.Button(self.ana_cerceve, text="Parola Üret", command=self.sifre_uret, width=30)
        self.sifre_uret_butonu.pack(pady=5)

    def kullanici_arayuzunu_goster(self, kullanici_adi):
        
        self.cerceve_temizle()
        self.ana_cerceve.pack(pady=20)

        self.web_sitesi_etiketi = tk.Label(self.ana_cerceve, text="Web Sitesi:")
        self.web_sitesi_etiketi.pack()

        self.web_sitesi_giris = tk.Entry(self.ana_cerceve)
        self.web_sitesi_giris.pack()

        self.kullanici_adi_etiketi = tk.Label(self.ana_cerceve, text="Kullanıcı Adı:")
        self.kullanici_adi_etiketi.pack()

        self.kullanici_adi_giris = tk.Entry(self.ana_cerceve)
        self.kullanici_adi_giris.pack()

        self.sifre_etiketi = tk.Label(self.ana_cerceve, text="Parola:")
        self.sifre_etiketi.pack()

        self.sifre_giris = tk.Entry(self.ana_cerceve)
        self.sifre_giris.pack()

        self.kaydet_butonu = tk.Button(self.ana_cerceve, text="Parolayı Kaydet", command=lambda: self.sifreyi_kaydet(kullanici_adi))
        self.kaydet_butonu.pack(pady=5)

        self.goruntule_butonu = tk.Button(self.ana_cerceve, text="Parolaları Görüntüle", command=lambda: self.sifreleri_goruntule(kullanici_adi))
        self.goruntule_butonu.pack(pady=5)

        self.sifre_uret_butonu = tk.Button(self.ana_cerceve, text="Parola Üret", command=self.kullanici_icin_sifre_uret)
        self.sifre_uret_butonu.pack(pady=5)

        self.cikis_yap_butonu = tk.Button(self.ana_cerceve, text="Çıkış Yap", command=self.ana_menuyu_goster)
        self.cikis_yap_butonu.pack(pady=5)

    def sifreyi_kaydet(self, kullanici_adi):
        
        web_sitesi = self.web_sitesi_giris.get()
        kullanici_adi_sifre = self.kullanici_adi_giris.get()
        sifre = self.sifre_giris.get()

        self.veritabani.sifre_ekle(kullanici_adi, web_sitesi, kullanici_adi_sifre, sifre)
        messagebox.showinfo("Bilgi", "Parola başarıyla kaydedildi")
        self.web_sitesi_giris.delete(0, tk.END)
        self.kullanici_adi_giris.delete(0, tk.END)
        self.sifre_giris.delete(0, tk.END)

    def sifreleri_goruntule(self, kullanici_adi):
        
        sifreler = self.veritabani.sifreleri_al(kullanici_adi)

        self.cerceve_temizle()
        self.ana_cerceve.pack(pady=20)

        self.agac = ttk.Treeview(self.ana_cerceve, columns=("Web Sitesi", "Kullanıcı Adı", "Parola"), show='headings')
        self.agac.heading("Web Sitesi", text="Web Sitesi")
        self.agac.heading("Kullanıcı Adı", text="Kullanıcı Adı")
        self.agac.heading("Parola", text="Parola")

        for sifre in sifreler:
            self.agac.insert("", tk.END, values=sifre)

        self.agac.bind("<Button-1>", self.agac_secim_yap)
        self.agac.pack()

        self.geri_butonu = tk.Button(self.ana_cerceve, text="Geri", command=lambda: self.kullanici_arayuzunu_goster(kullanici_adi))
        self.geri_butonu.pack(pady=5)

    def agac_secim_yap(self, event):
        
        item = self.agac.identify_row(event.y)
        column = self.agac.identify_column(event.x)
        if item and column:
            column_index = int(column[1:]) - 1
            cell_value = self.agac.item(item, 'values')[column_index]
            self.pano_ya_kopyala(cell_value)

    def kullanici_icin_sifre_uret(self):
        try:
            uzunluk = int(simpledialog.askstring("Parola Uzunluğu", "Parola uzunluğunu girin:"))
            if uzunluk <= 0:  
                messagebox.showerror("Hata", "Geçersiz parola uzunluğu")
                return
            sifre = self.guclu_sifre_uret(uzunluk)
            self.sifre_giris.delete(0, tk.END)
            self.sifre_giris.insert(0, sifre)
        except ValueError:
            messagebox.showerror("Hata", "Geçersiz parola uzunluğu")

root = tk.Tk()
app = SifreYoneticisiUygulamasi(root)
root.mainloop()
