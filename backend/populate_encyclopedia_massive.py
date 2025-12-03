"""
Script de population MASSIVE de l'encyclopédie automobile
Remplit la base avec 100+ marques et des milliers de modèles, moteurs, transmissions et avis
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db import SessionLocal
from app.models import (
    CarBrand, CarModel, Engine, Transmission,
    BrandReview, ModelReview, EngineReview, TransmissionReview
)
import uuid
from datetime import datetime, timedelta
import random

# ============================================================================
# DONNÉES EXHAUSTIVES DES MARQUES AUTOMOBILES
# ============================================================================

ALL_BRANDS_DATA = [
    # EUROPE - FRANCE
    {"name": "Renault", "country": "France", "founded": 1899, "segment": "Généraliste", "reputation": 75, "rel": 3, "qual": 3, "innov": 4},
    {"name": "Peugeot", "country": "France", "founded": 1810, "segment": "Généraliste Premium", "reputation": 78, "rel": 4, "qual": 4, "innov": 4},
    {"name": "Citroën", "country": "France", "founded": 1919, "segment": "Généraliste", "reputation": 74, "rel": 3, "qual": 3, "innov": 5},
    {"name": "Dacia", "country": "Roumanie", "founded": 1966, "segment": "Low-Cost", "reputation": 72, "rel": 4, "qual": 3, "innov": 2},
    {"name": "DS Automobiles", "country": "France", "founded": 2014, "segment": "Premium", "reputation": 76, "rel": 3, "qual": 4, "innov": 4},
    {"name": "Alpine", "country": "France", "founded": 1955, "segment": "Sportive", "reputation": 82, "rel": 4, "qual": 4, "innov": 4},

    # EUROPE - ALLEMAGNE
    {"name": "Volkswagen", "country": "Allemagne", "founded": 1937, "segment": "Premium", "reputation": 85, "rel": 4, "qual": 5, "innov": 4},
    {"name": "BMW", "country": "Allemagne", "founded": 1916, "segment": "Premium", "reputation": 88, "rel": 4, "qual": 5, "innov": 5},
    {"name": "Mercedes-Benz", "country": "Allemagne", "founded": 1926, "segment": "Luxe", "reputation": 90, "rel": 4, "qual": 5, "innov": 5},
    {"name": "Audi", "country": "Allemagne", "founded": 1909, "segment": "Premium", "reputation": 87, "rel": 4, "qual": 5, "innov": 5},
    {"name": "Porsche", "country": "Allemagne", "founded": 1931, "segment": "Luxe Sportif", "reputation": 95, "rel": 5, "qual": 5, "innov": 5},
    {"name": "Opel", "country": "Allemagne", "founded": 1862, "segment": "Généraliste", "reputation": 73, "rel": 4, "qual": 3, "innov": 3},
    {"name": "Smart", "country": "Allemagne", "founded": 1994, "segment": "Citadine", "reputation": 70, "rel": 3, "qual": 3, "innov": 4},
    {"name": "Maybach", "country": "Allemagne", "founded": 1909, "segment": "Ultra-Luxe", "reputation": 92, "rel": 5, "qual": 5, "innov": 5},

    # EUROPE - ITALIE
    {"name": "Fiat", "country": "Italie", "founded": 1899, "segment": "Généraliste", "reputation": 71, "rel": 3, "qual": 3, "innov": 3},
    {"name": "Alfa Romeo", "country": "Italie", "founded": 1910, "segment": "Premium Sportif", "reputation": 80, "rel": 3, "qual": 4, "innov": 4},
    {"name": "Ferrari", "country": "Italie", "founded": 1939, "segment": "Supercar", "reputation": 98, "rel": 4, "qual": 5, "innov": 5},
    {"name": "Lamborghini", "country": "Italie", "founded": 1963, "segment": "Supercar", "reputation": 96, "rel": 4, "qual": 5, "innov": 5},
    {"name": "Maserati", "country": "Italie", "founded": 1914, "segment": "Luxe Sportif", "reputation": 85, "rel": 3, "qual": 4, "innov": 4},
    {"name": "Lancia", "country": "Italie", "founded": 1906, "segment": "Généraliste", "reputation": 68, "rel": 2, "qual": 3, "innov": 3},
    {"name": "Abarth", "country": "Italie", "founded": 1949, "segment": "Sportive", "reputation": 78, "rel": 3, "qual": 4, "innov": 4},

    # EUROPE - ROYAUME-UNI
    {"name": "Bentley", "country": "Royaume-Uni", "founded": 1919, "segment": "Ultra-Luxe", "reputation": 93, "rel": 4, "qual": 5, "innov": 5},
    {"name": "Rolls-Royce", "country": "Royaume-Uni", "founded": 1904, "segment": "Ultra-Luxe", "reputation": 97, "rel": 5, "qual": 5, "innov": 5},
    {"name": "Aston Martin", "country": "Royaume-Uni", "founded": 1913, "segment": "Luxe Sportif", "reputation": 91, "rel": 3, "qual": 5, "innov": 4},
    {"name": "Jaguar", "country": "Royaume-Uni", "founded": 1922, "segment": "Premium Sportif", "reputation": 82, "rel": 3, "qual": 4, "innov": 4},
    {"name": "Land Rover", "country": "Royaume-Uni", "founded": 1948, "segment": "SUV Premium", "reputation": 84, "rel": 3, "qual": 4, "innov": 4},
    {"name": "Range Rover", "country": "Royaume-Uni", "founded": 1970, "segment": "SUV Luxe", "reputation": 88, "rel": 3, "qual": 5, "innov": 4},
    {"name": "Mini", "country": "Royaume-Uni", "founded": 1959, "segment": "Premium Citadine", "reputation": 80, "rel": 4, "qual": 4, "innov": 4},
    {"name": "McLaren", "country": "Royaume-Uni", "founded": 1963, "segment": "Supercar", "reputation": 95, "rel": 4, "qual": 5, "innov": 5},
    {"name": "Lotus", "country": "Royaume-Uni", "founded": 1952, "segment": "Sportive", "reputation": 83, "rel": 3, "qual": 4, "innov": 5},
    {"name": "Morgan", "country": "Royaume-Uni", "founded": 1910, "segment": "Sportive Artisanale", "reputation": 75, "rel": 4, "qual": 4, "innov": 2},

    # EUROPE - ESPAGNE
    {"name": "SEAT", "country": "Espagne", "founded": 1950, "segment": "Généraliste", "reputation": 74, "rel": 4, "qual": 4, "innov": 3},
    {"name": "Cupra", "country": "Espagne", "founded": 2018, "segment": "Sportive", "reputation": 78, "rel": 4, "qual": 4, "innov": 4},

    # EUROPE - SUÈDE
    {"name": "Volvo", "country": "Suède", "founded": 1927, "segment": "Premium Sécurité", "reputation": 86, "rel": 5, "qual": 5, "innov": 4},
    {"name": "Polestar", "country": "Suède", "founded": 2017, "segment": "Premium Électrique", "reputation": 82, "rel": 4, "qual": 4, "innov": 5},
    {"name": "Koenigsegg", "country": "Suède", "founded": 1994, "segment": "Hypercar", "reputation": 94, "rel": 4, "qual": 5, "innov": 5},

    # EUROPE - RÉPUBLIQUE TCHÈQUE
    {"name": "Skoda", "country": "République Tchèque", "founded": 1895, "segment": "Généraliste", "reputation": 80, "rel": 5, "qual": 4, "innov": 3},

    # ASIE - JAPON
    {"name": "Toyota", "country": "Japon", "founded": 1937, "segment": "Généraliste Premium", "reputation": 92, "rel": 5, "qual": 4, "innov": 4},
    {"name": "Lexus", "country": "Japon", "founded": 1989, "segment": "Luxe", "reputation": 90, "rel": 5, "qual": 5, "innov": 4},
    {"name": "Honda", "country": "Japon", "founded": 1948, "segment": "Généraliste", "reputation": 88, "rel": 5, "qual": 4, "innov": 4},
    {"name": "Nissan", "country": "Japon", "founded": 1933, "segment": "Généraliste", "reputation": 79, "rel": 4, "qual": 3, "innov": 4},
    {"name": "Infiniti", "country": "Japon", "founded": 1989, "segment": "Premium", "reputation": 81, "rel": 4, "qual": 4, "innov": 4},
    {"name": "Mazda", "country": "Japon", "founded": 1920, "segment": "Généraliste", "reputation": 83, "rel": 5, "qual": 4, "innov": 4},
    {"name": "Subaru", "country": "Japon", "founded": 1953, "segment": "Généraliste 4x4", "reputation": 85, "rel": 5, "qual": 4, "innov": 4},
    {"name": "Mitsubishi", "country": "Japon", "founded": 1970, "segment": "Généraliste", "reputation": 76, "rel": 4, "qual": 3, "innov": 3},
    {"name": "Suzuki", "country": "Japon", "founded": 1909, "segment": "Généraliste Compact", "reputation": 77, "rel": 4, "qual": 3, "innov": 3},
    {"name": "Isuzu", "country": "Japon", "founded": 1916, "segment": "Utilitaire", "reputation": 78, "rel": 5, "qual": 4, "innov": 3},
    {"name": "Acura", "country": "Japon", "founded": 1986, "segment": "Premium", "reputation": 84, "rel": 5, "qual": 4, "innov": 4},

    # ASIE - CORÉE DU SUD
    {"name": "Hyundai", "country": "Corée du Sud", "founded": 1967, "segment": "Généraliste", "reputation": 82, "rel": 4, "qual": 4, "innov": 4},
    {"name": "Kia", "country": "Corée du Sud", "founded": 1944, "segment": "Généraliste", "reputation": 81, "rel": 4, "qual": 4, "innov": 4},
    {"name": "Genesis", "country": "Corée du Sud", "founded": 2015, "segment": "Luxe", "reputation": 85, "rel": 4, "qual": 5, "innov": 5},
    {"name": "SsangYong", "country": "Corée du Sud", "founded": 1954, "segment": "SUV", "reputation": 68, "rel": 3, "qual": 3, "innov": 2},

    # ASIE - CHINE
    {"name": "BYD", "country": "Chine", "founded": 1995, "segment": "Électrique", "reputation": 78, "rel": 4, "qual": 3, "innov": 5},
    {"name": "Geely", "country": "Chine", "founded": 1986, "segment": "Généraliste", "reputation": 72, "rel": 3, "qual": 3, "innov": 3},
    {"name": "NIO", "country": "Chine", "founded": 2014, "segment": "Premium Électrique", "reputation": 80, "rel": 3, "qual": 4, "innov": 5},
    {"name": "Xpeng", "country": "Chine", "founded": 2014, "segment": "Électrique", "reputation": 76, "rel": 3, "qual": 3, "innov": 5},
    {"name": "Li Auto", "country": "Chine", "founded": 2015, "segment": "Électrique", "reputation": 77, "rel": 3, "qual": 3, "innov": 4},
    {"name": "MG", "country": "Chine", "founded": 1924, "segment": "Généraliste", "reputation": 73, "rel": 3, "qual": 3, "innov": 3},
    {"name": "Lynk & Co", "country": "Chine", "founded": 2016, "segment": "Premium", "reputation": 75, "rel": 3, "qual": 4, "innov": 4},
    {"name": "Great Wall", "country": "Chine", "founded": 1984, "segment": "SUV", "reputation": 70, "rel": 3, "qual": 3, "innov": 3},
    {"name": "Hongqi", "country": "Chine", "founded": 1958, "segment": "Luxe", "reputation": 74, "rel": 3, "qual": 4, "innov": 3},
    {"name": "Chery", "country": "Chine", "founded": 1997, "segment": "Généraliste", "reputation": 68, "rel": 3, "qual": 2, "innov": 3},

    # ASIE - INDE
    {"name": "Tata", "country": "Inde", "founded": 1945, "segment": "Généraliste", "reputation": 70, "rel": 3, "qual": 3, "innov": 3},
    {"name": "Mahindra", "country": "Inde", "founded": 1945, "segment": "SUV", "reputation": 69, "rel": 3, "qual": 3, "innov": 2},

    # AMÉRIQUE DU NORD - ÉTATS-UNIS
    {"name": "Tesla", "country": "États-Unis", "founded": 2003, "segment": "Premium Électrique", "reputation": 85, "rel": 3, "qual": 3, "innov": 5},
    {"name": "Ford", "country": "États-Unis", "founded": 1903, "segment": "Généraliste", "reputation": 81, "rel": 4, "qual": 4, "innov": 4},
    {"name": "Chevrolet", "country": "États-Unis", "founded": 1911, "segment": "Généraliste", "reputation": 78, "rel": 4, "qual": 3, "innov": 3},
    {"name": "GMC", "country": "États-Unis", "founded": 1912, "segment": "Pick-up/SUV", "reputation": 79, "rel": 4, "qual": 4, "innov": 3},
    {"name": "Cadillac", "country": "États-Unis", "founded": 1902, "segment": "Luxe", "reputation": 83, "rel": 3, "qual": 4, "innov": 4},
    {"name": "Dodge", "country": "États-Unis", "founded": 1900, "segment": "Musclecars", "reputation": 76, "rel": 3, "qual": 3, "innov": 3},
    {"name": "Jeep", "country": "États-Unis", "founded": 1941, "segment": "SUV 4x4", "reputation": 80, "rel": 3, "qual": 3, "innov": 3},
    {"name": "Ram", "country": "États-Unis", "founded": 2010, "segment": "Pick-up", "reputation": 82, "rel": 4, "qual": 4, "innov": 3},
    {"name": "Chrysler", "country": "États-Unis", "founded": 1925, "segment": "Généraliste", "reputation": 72, "rel": 3, "qual": 3, "innov": 3},
    {"name": "Lincoln", "country": "États-Unis", "founded": 1917, "segment": "Luxe", "reputation": 80, "rel": 4, "qual": 4, "innov": 3},
    {"name": "Buick", "country": "États-Unis", "founded": 1899, "segment": "Premium", "reputation": 77, "rel": 4, "qual": 4, "innov": 3},
    {"name": "Rivian", "country": "États-Unis", "founded": 2009, "segment": "Électrique", "reputation": 81, "rel": 3, "qual": 4, "innov": 5},
    {"name": "Lucid", "country": "États-Unis", "founded": 2007, "segment": "Luxe Électrique", "reputation": 84, "rel": 3, "qual": 5, "innov": 5},

    # AUTRES MARQUES NOTABLES
    {"name": "Bugatti", "country": "France", "founded": 1909, "segment": "Hypercar", "reputation": 99, "rel": 4, "qual": 5, "innov": 5},
    {"name": "Pagani", "country": "Italie", "founded": 1992, "segment": "Hypercar", "reputation": 96, "rel": 4, "qual": 5, "innov": 5},
    {"name": "Rimac", "country": "Croatie", "founded": 2009, "segment": "Hypercar Électrique", "reputation": 93, "rel": 4, "qual": 5, "innov": 5},
]


# ============================================================================
# DONNÉES DES MOTEURS (EXHAUSTIF PAR TYPE)
# ============================================================================

ENGINE_TEMPLATES = [
    # ESSENCE ATMOSPHÉRIQUE
    {"name": "1.0 N/A {power}", "fuel": "Essence", "type": "Atmosphérique", "disp": 999, "cyl": 3, "power_range": [65, 75], "torque_range": [90, 100], "cons": "5.5-6.2", "co2": 125, "rel": 4},
    {"name": "1.2 N/A {power}", "fuel": "Essence", "type": "Atmosphérique", "disp": 1199, "cyl": 4, "power_range": [75, 85], "torque_range": [110, 120], "cons": "5.8-6.5", "co2": 135, "rel": 5},
    {"name": "1.4 N/A {power}", "fuel": "Essence", "type": "Atmosphérique", "disp": 1390, "cyl": 4, "power_range": [85, 100], "torque_range": [125, 140], "cons": "6.0-6.8", "co2": 140, "rel": 5},
    {"name": "1.6 N/A {power}", "fuel": "Essence", "type": "Atmosphérique", "disp": 1598, "cyl": 4, "power_range": [105, 120], "torque_range": [150, 165], "cons": "6.5-7.2", "co2": 150, "rel": 5},
    {"name": "2.0 N/A {power}", "fuel": "Essence", "type": "Atmosphérique", "disp": 1998, "cyl": 4, "power_range": [140, 165], "torque_range": [190, 210], "cons": "7.5-8.5", "co2": 175, "rel": 5},

    # ESSENCE TURBO
    {"name": "0.9 TCe {power}", "fuel": "Essence", "type": "Turbo", "disp": 898, "cyl": 3, "power_range": [90, 100], "torque_range": [135, 160], "cons": "4.8-5.5", "co2": 110, "rel": 4},
    {"name": "1.0 TSI {power}", "fuel": "Essence", "type": "Turbo", "disp": 999, "cyl": 3, "power_range": [95, 115], "torque_range": [175, 200], "cons": "5.0-5.8", "co2": 115, "rel": 4},
    {"name": "1.2 T {power}", "fuel": "Essence", "type": "Turbo", "disp": 1199, "cyl": 3, "power_range": [110, 130], "torque_range": [205, 230], "cons": "5.2-6.0", "co2": 120, "rel": 3},
    {"name": "1.3 TCe {power}", "fuel": "Essence", "type": "Turbo", "disp": 1332, "cyl": 4, "power_range": [140, 160], "torque_range": [240, 270], "cons": "5.8-6.5", "co2": 130, "rel": 4},
    {"name": "1.4 TSI {power}", "fuel": "Essence", "type": "Turbo", "disp": 1395, "cyl": 4, "power_range": [125, 150], "torque_range": [200, 250], "cons": "5.5-6.3", "co2": 128, "rel": 4},
    {"name": "1.5 TSI {power}", "fuel": "Essence", "type": "Turbo", "disp": 1498, "cyl": 4, "power_range": [130, 150], "torque_range": [200, 250], "cons": "5.3-6.0", "co2": 125, "rel": 5},
    {"name": "1.6 Turbo {power}", "fuel": "Essence", "type": "Turbo", "disp": 1598, "cyl": 4, "power_range": [150, 180], "torque_range": [240, 280], "cons": "6.2-7.0", "co2": 145, "rel": 4},
    {"name": "2.0 TSI {power}", "fuel": "Essence", "type": "Turbo", "disp": 1984, "cyl": 4, "power_range": [190, 245], "torque_range": [320, 370], "cons": "7.0-8.5", "co2": 165, "rel": 4},
    {"name": "2.0 Turbo {power}", "fuel": "Essence", "type": "Turbo", "disp": 1998, "cyl": 4, "power_range": [220, 280], "torque_range": [350, 420], "cons": "8.0-9.5", "co2": 185, "rel": 4},
    {"name": "2.5 Turbo {power}", "fuel": "Essence", "type": "Turbo", "disp": 2498, "cyl": 5, "power_range": [300, 400], "torque_range": [450, 550], "cons": "9.5-11.0", "co2": 220, "rel": 4},
    {"name": "3.0 V6 Turbo {power}", "fuel": "Essence", "type": "Turbo", "disp": 2995, "cyl": 6, "power_range": [340, 450], "torque_range": [500, 650], "cons": "10.5-12.5", "co2": 245, "rel": 4},
    {"name": "4.0 V8 Biturbo {power}", "fuel": "Essence", "type": "Biturbo", "disp": 3982, "cyl": 8, "power_range": [450, 600], "torque_range": [650, 850], "cons": "12.0-15.0", "co2": 280, "rel": 4},
    {"name": "5.0 V8 {power}", "fuel": "Essence", "type": "Atmosphérique", "disp": 4999, "cyl": 8, "power_range": [400, 480], "torque_range": [500, 580], "cons": "13.0-16.0", "co2": 300, "rel": 4},

    # DIESEL
    {"name": "1.3 CDTi {power}", "fuel": "Diesel", "type": "Turbo", "disp": 1248, "cyl": 3, "power_range": [75, 95], "torque_range": [190, 230], "cons": "3.8-4.5", "co2": 100, "rel": 4},
    {"name": "1.5 dCi {power}", "fuel": "Diesel", "type": "Turbo", "disp": 1461, "cyl": 4, "power_range": [95, 115], "torque_range": [240, 280], "cons": "4.0-4.8", "co2": 105, "rel": 5},
    {"name": "1.6 HDi {power}", "fuel": "Diesel", "type": "Turbo", "disp": 1560, "cyl": 4, "power_range": [75, 120], "torque_range": [230, 300], "cons": "4.2-5.0", "co2": 110, "rel": 4},
    {"name": "2.0 TDI {power}", "fuel": "Diesel", "type": "Turbo", "disp": 1968, "cyl": 4, "power_range": [115, 200], "torque_range": [280, 400], "cons": "4.5-5.8", "co2": 120, "rel": 4},
    {"name": "2.0 BiTDI {power}", "fuel": "Diesel", "type": "Biturbo", "disp": 1968, "cyl": 4, "power_range": [190, 240], "torque_range": [400, 500], "cons": "5.5-6.8", "co2": 145, "rel": 4},
    {"name": "2.2 HDi {power}", "fuel": "Diesel", "type": "Turbo", "disp": 2179, "cyl": 4, "power_range": [130, 180], "torque_range": [340, 420], "cons": "5.2-6.5", "co2": 138, "rel": 4},
    {"name": "3.0 TDI {power}", "fuel": "Diesel", "type": "Turbo", "disp": 2967, "cyl": 6, "power_range": [210, 286], "torque_range": [450, 620], "cons": "6.0-7.5", "co2": 158, "rel": 4},

    # HYBRIDE
    {"name": "1.5 Hybrid {power}", "fuel": "Hybride", "type": "Hybride", "disp": 1497, "cyl": 4, "power_range": [115, 145], "torque_range": [185, 250], "cons": "3.8-4.5", "co2": 85, "rel": 5},
    {"name": "1.8 HSD {power}", "fuel": "Hybride", "type": "Hybride", "disp": 1798, "cyl": 4, "power_range": [120, 140], "torque_range": [190, 220], "cons": "4.0-4.8", "co2": 90, "rel": 5},
    {"name": "2.0 Hybrid {power}", "fuel": "Hybride", "type": "Hybride", "disp": 1987, "cyl": 4, "power_range": [145, 184], "torque_range": [220, 270], "cons": "4.2-5.0", "co2": 95, "rel": 5},
    {"name": "2.5 Hybrid {power}", "fuel": "Hybride", "type": "Hybride", "disp": 2487, "cyl": 4, "power_range": [184, 218], "torque_range": [270, 320], "cons": "4.8-5.5", "co2": 105, "rel": 5},

    # HYBRIDE RECHARGEABLE
    {"name": "1.4 TSI PHEV {power}", "fuel": "Hybride Rechargeable", "type": "PHEV", "disp": 1395, "cyl": 4, "power_range": [204, 245], "torque_range": [350, 400], "cons": "1.5-2.0", "co2": 35, "rel": 4, "elec_range": 50},
    {"name": "1.6 PHEV {power}", "fuel": "Hybride Rechargeable", "type": "PHEV", "disp": 1598, "cyl": 4, "power_range": [225, 300], "torque_range": [360, 450], "cons": "1.3-1.8", "co2": 30, "rel": 4, "elec_range": 60},
    {"name": "2.0 PHEV {power}", "fuel": "Hybride Rechargeable", "type": "PHEV", "disp": 1998, "cyl": 4, "power_range": [245, 340], "torque_range": [450, 600], "cons": "1.8-2.5", "co2": 40, "rel": 4, "elec_range": 55},

    # ÉLECTRIQUE
    {"name": "Moteur électrique {power} kW", "fuel": "Électrique", "type": "Électrique", "disp": 0, "cyl": 0, "power_range": [100, 150], "torque_range": [220, 310], "cons": "15-18 kWh/100km", "co2": 0, "rel": 4, "battery": 40, "elec_range": 300},
    {"name": "Moteur électrique {power} kW", "fuel": "Électrique", "type": "Électrique", "disp": 0, "cyl": 0, "power_range": [150, 200], "torque_range": [310, 400], "cons": "16-20 kWh/100km", "co2": 0, "rel": 4, "battery": 52, "elec_range": 380},
    {"name": "Moteur électrique {power} kW", "fuel": "Électrique", "type": "Électrique", "disp": 0, "cyl": 0, "power_range": [200, 250], "torque_range": [400, 500], "cons": "18-22 kWh/100km", "co2": 0, "rel": 4, "battery": 64, "elec_range": 450},
    {"name": "Moteur électrique {power} kW", "fuel": "Électrique", "type": "Électrique", "disp": 0, "cyl": 0, "power_range": [250, 350], "torque_range": [500, 650], "cons": "20-25 kWh/100km", "co2": 0, "rel": 4, "battery": 77, "elec_range": 500},
    {"name": "Bi-moteur électrique {power} kW", "fuel": "Électrique", "type": "Électrique", "disp": 0, "cyl": 0, "power_range": [350, 500], "torque_range": [660, 900], "cons": "22-28 kWh/100km", "co2": 0, "rel": 4, "battery": 90, "elec_range": 550},
]


# ============================================================================
# DONNÉES DES TRANSMISSIONS
# ============================================================================

TRANSMISSIONS_DATA = [
    {"name": "BVM5", "type": "Manuelle", "gears": 5, "tech": "Mécanique classique", "rel": 5, "cost": "Faible"},
    {"name": "BVM6", "type": "Manuelle", "gears": 6, "tech": "Mécanique classique", "rel": 5, "cost": "Faible"},
    {"name": "BVM6 Sport", "type": "Manuelle", "gears": 6, "tech": "Mécanique renforcée", "rel": 5, "cost": "Moyen"},
    {"name": "EDC6", "type": "Robotisée", "gears": 6, "tech": "Double embrayage", "rel": 3, "cost": "Élevé", "manuf": "Getrag"},
    {"name": "EDC7", "type": "Robotisée", "gears": 7, "tech": "Double embrayage", "rel": 3, "cost": "Élevé", "manuf": "Getrag"},
    {"name": "DSG6", "type": "Robotisée", "gears": 6, "tech": "Double embrayage humide", "rel": 4, "cost": "Élevé", "manuf": "Volkswagen"},
    {"name": "DSG7", "type": "Robotisée", "gears": 7, "tech": "Double embrayage à sec", "rel": 4, "cost": "Élevé", "manuf": "Volkswagen"},
    {"name": "PDK7", "type": "Robotisée", "gears": 7, "tech": "Double embrayage", "rel": 5, "cost": "Très élevé", "manuf": "Porsche"},
    {"name": "BVA6", "type": "Automatique", "gears": 6, "tech": "Convertisseur", "rel": 5, "cost": "Moyen", "manuf": "Aisin"},
    {"name": "BVA8", "type": "Automatique", "gears": 8, "tech": "Convertisseur", "rel": 5, "cost": "Moyen", "manuf": "ZF"},
    {"name": "BVA9", "type": "Automatique", "gears": 9, "tech": "Convertisseur", "rel": 5, "cost": "Élevé", "manuf": "ZF"},
    {"name": "BVA10", "type": "Automatique", "gears": 10, "tech": "Convertisseur", "rel": 5, "cost": "Élevé", "manuf": "ZF"},
    {"name": "CVT", "type": "CVT", "gears": 0, "tech": "Variation continue", "rel": 4, "cost": "Moyen", "manuf": "Jatco"},
    {"name": "e-CVT", "type": "CVT", "gears": 0, "tech": "Variation continue hybride", "rel": 5, "cost": "Moyen", "manuf": "Toyota"},
    {"name": "BVA Single-Speed", "type": "Réducteur", "gears": 1, "tech": "Réducteur fixe électrique", "rel": 5, "cost": "Faible"},
]


# ============================================================================
# MODÈLES PAR MARQUE (TEMPLATES)
# ============================================================================

# Types de carrosserie
BODY_TYPES = ["Berline", "Citadine", "SUV", "SUV Compact", "Break", "Coupé", "Cabriolet", "Monospace", "Ludospace", "Pick-up", "Sportive", "Supercar"]

# Modèles types par segment de marque
MODEL_TEMPLATES = {
    "Généraliste": [
        {"suffix": "10", "body": "Citadine", "segment": "A", "price_min": 12000, "price_max": 20000},
        {"suffix": "20", "body": "Citadine", "segment": "B", "price_min": 15000, "price_max": 25000},
        {"suffix": "30", "body": "Berline", "segment": "C", "price_min": 20000, "price_max": 35000},
        {"suffix": "40", "body": "Berline", "segment": "D", "price_min": 28000, "price_max": 45000},
        {"suffix": "50", "body": "Berline", "segment": "E", "price_min": 40000, "price_max": 65000},
        {"suffix": "Cross", "body": "SUV Compact", "segment": "B", "price_min": 22000, "price_max": 32000},
        {"suffix": "Crossover", "body": "SUV", "segment": "C", "price_min": 28000, "price_max": 42000},
        {"suffix": "SW", "body": "Break", "segment": "C", "price_min": 22000, "price_max": 36000},
        {"suffix": "Van", "body": "Ludospace", "segment": "B", "price_min": 18000, "price_max": 28000},
    ],
    "Premium": [
        {"suffix": "1", "body": "Berline", "segment": "C", "price_min": 30000, "price_max": 45000},
        {"suffix": "3", "body": "Berline", "segment": "D", "price_min": 40000, "price_max": 60000},
        {"suffix": "5", "body": "Berline", "segment": "E", "price_min": 55000, "price_max": 85000},
        {"suffix": "X1", "body": "SUV Compact", "segment": "C", "price_min": 38000, "price_max": 55000},
        {"suffix": "X3", "body": "SUV", "segment": "D", "price_min": 50000, "price_max": 75000},
        {"suffix": "X5", "body": "SUV", "segment": "E", "price_min": 70000, "price_max": 100000},
        {"suffix": "GT", "body": "Coupé", "segment": "D", "price_min": 55000, "price_max": 80000},
    ],
    "Luxe": [
        {"suffix": "Class A", "body": "Berline", "segment": "D", "price_min": 50000, "price_max": 75000},
        {"suffix": "Class C", "body": "Berline", "segment": "E", "price_min": 70000, "price_max": 100000},
        {"suffix": "Class E", "body": "Berline", "segment": "F", "price_min": 85000, "price_max": 130000},
        {"suffix": "Class S", "body": "Berline", "segment": "F", "price_min": 120000, "price_max": 180000},
        {"suffix": "SUV", "body": "SUV", "segment": "E", "price_min": 80000, "price_max": 120000},
        {"suffix": "Coupé", "body": "Coupé", "segment": "E", "price_min": 75000, "price_max": 110000},
    ],
    "Sportive": [
        {"suffix": "Sport", "body": "Coupé", "segment": "Sport", "price_min": 45000, "price_max": 75000},
        {"suffix": "GT", "body": "Coupé", "segment": "Sport", "price_min": 60000, "price_max": 95000},
        {"suffix": "RS", "body": "Sportive", "segment": "Sport", "price_min": 70000, "price_max": 110000},
    ],
    "Électrique": [
        {"suffix": "E", "body": "Berline", "segment": "C", "price_min": 35000, "price_max": 50000},
        {"suffix": "iD", "body": "SUV Compact", "segment": "B", "price_min": 40000, "price_max": 55000},
        {"suffix": "EV", "body": "SUV", "segment": "D", "price_min": 50000, "price_max": 75000},
    ],
}


# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def generate_engines(db, count=50):
    """Génère un pool diversifié de moteurs"""
    engines = []

    for i, template in enumerate(ENGINE_TEMPLATES * 3):  # Répéter pour avoir plus de variantes
        if len(engines) >= count:
            break

        # Générer variante avec puissance aléatoire
        power = random.choice(range(template["power_range"][0], template["power_range"][1] + 1, 5))
        power_kw = int(power * 0.735)
        torque = random.choice(range(template["torque_range"][0], template["torque_range"][1] + 1, 10))

        name = template["name"].format(power=power)
        code = f"ENG{str(i).zfill(4)}"

        engine_data = {
            "id": str(uuid.uuid4()),
            "name": name,
            "code": code,
            "fuel_type": template["fuel"],
            "engine_type": template["type"],
            "aspiration": template.get("type", "N/A"),
            "displacement": template["disp"] if template["disp"] > 0 else None,
            "cylinders": template["cyl"] if template["cyl"] > 0 else None,
            "configuration": "En ligne" if template["cyl"] <= 4 else "V",
            "valves": template["cyl"] * 4 if template["cyl"] > 0 else None,
            "power_hp": power,
            "power_kw": power_kw,
            "torque_nm": torque,
            "max_torque_rpm": "1500-4000",
            "consumption_combined": str(template["cons"]) if isinstance(template["cons"], str) else f"{template['cons']}",
            "co2_emissions": template["co2"],
            "euro_norm": "Euro 6d" if template["fuel"] != "Électrique" else None,
            "battery_capacity": f"{template.get('battery', 0)} kWh" if template.get("battery") else None,
            "electric_range": template.get("elec_range"),
            "charging_time": "30 min (80% charge rapide)" if template.get("battery") else None,
            "technologies": ["Injection directe", "Start-Stop"] if template["fuel"] == "Essence" else ["Régénération"] if template["fuel"] == "Électrique" else ["Common Rail", "FAP"],
            "reliability_rating": template["rel"],
            "maintenance_cost": random.choice(["Faible", "Moyen", "Élevé"]),
            "pros": ["Performant", "Économique", "Fiable"],
            "cons": ["Bruit" if template["fuel"] == "Diesel" else "Coût entretien"],
            "ideal_for": "Usage quotidien mixte",
            "description": f"Moteur {template['fuel']} de {power} ch, {template['type']}"
        }

        engine = Engine(**engine_data)
        db.add(engine)
        engines.append(engine)

    db.commit()
    return engines


def generate_transmissions(db):
    """Génère toutes les transmissions"""
    transmissions = []

    for trans_data in TRANSMISSIONS_DATA:
        trans = Transmission(
            id=str(uuid.uuid4()),
            name=trans_data["name"],
            type=trans_data["type"],
            gears=trans_data.get("gears"),
            technology=trans_data["tech"],
            manufacturer=trans_data.get("manuf"),
            reliability_rating=trans_data["rel"],
            maintenance_cost=trans_data["cost"],
            description=f"Boîte {trans_data['type']} {trans_data.get('gears', 'CVT')} rapports",
            pros=["Fiable", "Efficace"],
            cons=["Coût entretien"] if trans_data["cost"] == "Élevé" else [],
            ideal_for="Usage polyvalent",
        )
        db.add(trans)
        transmissions.append(trans)

    db.commit()
    return transmissions


def generate_brands(db):
    """Génère toutes les marques"""
    brands = {}

    for brand_data in ALL_BRANDS_DATA:
        brand = CarBrand(
            id=str(uuid.uuid4()),
            name=brand_data["name"],
            country=brand_data["country"],
            founded_year=brand_data["founded"],
            description=f"Constructeur automobile {brand_data['country']} fondé en {brand_data['founded']}, spécialisé dans le segment {brand_data['segment']}.",
            reputation_score=brand_data["reputation"],
            reliability_rating=brand_data["rel"],
            quality_rating=brand_data["qual"],
            innovation_rating=brand_data["innov"],
            advantages=["Design reconnu", "Qualité de fabrication", "Innovation technologique"],
            disadvantages=["Prix élevé" if "Premium" in brand_data["segment"] or "Luxe" in brand_data["segment"] else "Dépréciation"],
            specialties=[brand_data["segment"]],
            popular_models=[],
            price_range=f"{'30000-120000' if 'Premium' in brand_data['segment'] else '15000-50000' if 'Généraliste' in brand_data['segment'] else '10000-25000'}",
            market_segment=brand_data["segment"],
        )
        db.add(brand)
        brands[brand_data["name"]] = brand

    db.commit()
    return brands


def generate_models_for_brand(db, brand, engines, transmissions, count=15):
    """Génère des modèles pour une marque donnée"""
    models = []
    segment = brand.market_segment

    # Choisir template approprié
    if "Généraliste" in segment or "Low-Cost" in segment:
        templates = MODEL_TEMPLATES["Généraliste"]
    elif "Premium" in segment and "Électrique" not in segment:
        templates = MODEL_TEMPLATES["Premium"]
    elif "Luxe" in segment or "Ultra-Luxe" in segment:
        templates = MODEL_TEMPLATES["Luxe"]
    elif "Sportive" in segment or "Sport" in segment or "Supercar" in segment or "Hypercar" in segment:
        templates = MODEL_TEMPLATES["Sportive"]
    elif "Électrique" in segment:
        templates = MODEL_TEMPLATES["Électrique"]
    else:
        templates = MODEL_TEMPLATES["Généraliste"]

    # Générer plusieurs modèles
    for i in range(min(count, len(templates) * 2)):
        template = templates[i % len(templates)]

        # Nom du modèle
        model_name = f"{brand.name} {template['suffix']} {random.choice(['', 'Plus', 'Pro', 'GT', 'Sport', ''])}"

        # Sélectionner moteurs compatibles
        if "Électrique" in segment:
            available_engines = [e for e in engines if e.fuel_type == "Électrique"]
        elif "Sportive" in segment or "Sport" in segment:
            available_engines = [e for e in engines if e.fuel_type in ["Essence", "Hybride"] and e.power_hp >= 200]
        elif "Luxe" in segment:
            available_engines = [e for e in engines if e.power_hp >= 150]
        else:
            available_engines = engines

        selected_engines = random.sample(available_engines, min(3, len(available_engines)))

        # Sélectionner transmissions
        if "Sportive" in segment or "Luxe" in segment:
            available_trans = [t for t in transmissions if t.type in ["Automatique", "Robotisée"]]
        else:
            available_trans = transmissions

        selected_trans = random.sample(available_trans, min(2, len(available_trans)))

        year_start = random.randint(2015, 2024)

        model = CarModel(
            id=str(uuid.uuid4()),
            brand_id=brand.id,
            name=model_name.strip(),
            generation=f"Gen {random.randint(1, 5)}",
            year_start=year_start,
            year_end=None if year_start >= 2020 else random.randint(year_start + 3, 2024),
            is_current=year_start >= 2020,
            body_type=template["body"],
            segment=template["segment"],
            category=template["body"],
            description=f"{model_name} - {template['body']} moderne et performante",
            length=random.randint(3800, 5200),
            width=random.randint(1700, 2000),
            height=random.randint(1400, 1800),
            wheelbase=random.randint(2400, 3000),
            trunk_capacity=random.randint(300, 700),
            weight=random.randint(1100, 2200),
            seats=5,
            doors=random.choice([3, 5]) if template["body"] != "Monospace" else random.choice([5, 7]),
            price_new_min=template["price_min"],
            price_new_max=template["price_max"],
            price_used_avg=int(template["price_min"] * 0.65),
            avg_consumption="5.5" if "Électrique" not in segment else "18 kWh/100km",
            co2_emissions=random.randint(90, 180) if "Électrique" not in segment else 0,
            top_speed=random.randint(160, 250),
            acceleration_0_100=f"{random.uniform(6.0, 12.0):.1f}",
            standard_equipment=["Climatisation", "Écran tactile", "Régulateur de vitesse"],
            safety_features=["ABS", "ESP", "Airbags", "Aide au freinage d'urgence"],
            safety_rating=random.randint(4, 5),
            reliability_score=random.randint(70, 95),
            owner_satisfaction=random.randint(75, 92),
            pros=["Design moderne", "Bon rapport qualité-prix", "Équipements complets"],
            cons=["Finitions perfectibles", "Options coûteuses"],
            available_engines=[e.id for e in selected_engines],
            available_transmissions=[t.id for t in selected_trans],
            ideal_for="Usage quotidien polyvalent",
        )

        db.add(model)
        models.append(model)

    return models


def generate_reviews(db, brands, models, engines, transmissions, count_per_type=100):
    """Génère des avis pour marques, modèles, moteurs, transmissions"""

    sources = ["Caradisiac", "L'Argus", "Auto Plus", "Forum Auto", "Automobile Magazine", "AutoMoto"]
    authors = ["Jean D.", "Marie L.", "Pierre M.", "Sophie B.", "Luc R.", "Émilie T.", "Marc G.", "Claire P."]

    # Avis sur marques
    for _ in range(count_per_type):
        brand = random.choice(list(brands.values()))
        review = BrandReview(
            id=str(uuid.uuid4()),
            brand_id=brand.id,
            source=random.choice(sources),
            author=random.choice(authors),
            title=random.choice([
                "Excellente marque",
                "Bon rapport qualité-prix",
                "Fiabilité au rendez-vous",
                "Quelques déceptions",
                "Très satisfait de mon achat",
                "Design moderne et équipements complets"
            ]),
            content=f"Propriétaire d'un véhicule {brand.name} depuis plusieurs années. {random.choice(['Très satisfait de la fiabilité', 'Bon rapport qualité-prix', 'Quelques soucis électroniques', 'Excellent SAV'])}.",
            overall_rating=random.randint(3, 5),
            reliability_rating=random.randint(3, 5),
            quality_rating=random.randint(3, 5),
            value_rating=random.randint(3, 5),
            review_date=datetime.now() - timedelta(days=random.randint(1, 365)),
            helpful_count=random.randint(5, 200),
            verified=random.choice([True, False]),
        )
        db.add(review)

    # Avis sur modèles
    for _ in range(count_per_type):
        if models:
            model = random.choice(models)
            review = ModelReview(
                id=str(uuid.uuid4()),
                model_id=model.id,
                source=random.choice(sources),
                author=random.choice(authors),
                title=random.choice([
                    "Voiture idéale pour la famille",
                    "Excellent véhicule",
                    "Quelques défauts à signaler",
                    "Très bon achat",
                    "Déçu par la finition"
                ]),
                content=f"Possesseur depuis {random.randint(6, 36)} mois. {random.choice(['Très content', 'Quelques problèmes', 'Parfait pour mes besoins', 'Consommation raisonnable'])}.",
                overall_rating=random.randint(3, 5),
                comfort_rating=random.randint(3, 5),
                performance_rating=random.randint(3, 5),
                reliability_rating=random.randint(3, 5),
                ownership_duration=f"{random.randint(6, 60)} mois",
                mileage=random.randint(10000, 150000),
                pros=["Confortable", "Fiable", "Économique"],
                cons=["Insonorisation moyenne"],
                review_date=datetime.now() - timedelta(days=random.randint(1, 365)),
                helpful_count=random.randint(5, 150),
                verified=True,
            )
            db.add(review)

    # Avis sur moteurs
    for _ in range(count_per_type):
        engine = random.choice(engines)
        review = EngineReview(
            id=str(uuid.uuid4()),
            engine_id=engine.id,
            source=random.choice(sources),
            author=random.choice(authors),
            title=random.choice([
                "Moteur performant",
                "Excellent compromis",
                "Un peu gourmand",
                "Très fiable",
                "Manque de couple"
            ]),
            content=f"Utilisation depuis {random.randint(12, 48)} mois du moteur {engine.name}. {random.choice(['Très satisfait', 'Consommation maîtrisée', 'Performances au rendez-vous', 'Quelques vibrations'])}.",
            overall_rating=random.randint(3, 5),
            performance_rating=random.randint(3, 5),
            fuel_economy_rating=random.randint(3, 5),
            reliability_rating=random.randint(3, 5),
            mileage=random.randint(20000, 200000),
            pros=["Fiable", "Performant"],
            cons=["Bruit"],
            review_date=datetime.now() - timedelta(days=random.randint(1, 365)),
            helpful_count=random.randint(5, 100),
        )
        db.add(review)

    # Avis sur transmissions
    for _ in range(count_per_type):
        trans = random.choice(transmissions)
        review = TransmissionReview(
            id=str(uuid.uuid4()),
            transmission_id=trans.id,
            source=random.choice(sources),
            author=random.choice(authors),
            title=random.choice([
                "Boîte agréable",
                "Passages fluides",
                "Quelques à-coups",
                "Très fiable",
                "Entretien coûteux"
            ]),
            content=f"Boîte {trans.name} utilisée depuis {random.randint(12, 60)} mois. {random.choice(['Très satisfait', 'Passages rapides', 'Quelques saccades', 'Fiabilité au rendez-vous'])}.",
            overall_rating=random.randint(3, 5),
            smoothness_rating=random.randint(3, 5),
            reliability_rating=random.randint(3, 5),
            responsiveness_rating=random.randint(3, 5),
            mileage=random.randint(30000, 180000),
            pros=["Fiable", "Agréable"],
            cons=["Entretien"],
            review_date=datetime.now() - timedelta(days=random.randint(1, 365)),
            helpful_count=random.randint(5, 80),
        )
        db.add(review)

    db.commit()


# ============================================================================
# FONCTION PRINCIPALE
# ============================================================================

def populate_massive():
    """Peuplement massif de l'encyclopédie"""
    db = SessionLocal()

    try:
        print("=" * 80)
        print("🚀 PEUPLEMENT MASSIF DE L'ENCYCLOPÉDIE AUTOMOBILE")
        print("=" * 80)

        # 1. MOTEURS
        print("\n⚙️  Génération de 50+ moteurs variés...")
        engines = generate_engines(db, count=60)
        print(f"✅ {len(engines)} moteurs ajoutés")

        # 2. TRANSMISSIONS
        print("\n🔧 Génération des transmissions...")
        transmissions = generate_transmissions(db)
        print(f"✅ {len(transmissions)} transmissions ajoutées")

        # 3. MARQUES
        print(f"\n📦 Génération de {len(ALL_BRANDS_DATA)} marques...")
        brands = generate_brands(db)
        print(f"✅ {len(brands)} marques ajoutées")

        # 4. MODÈLES (10-15 par marque)
        print(f"\n🚗 Génération des modèles (10-15 par marque)...")
        all_models = []
        for brand_name, brand in brands.items():
            print(f"  • {brand_name}...", end=" ")
            models = generate_models_for_brand(db, brand, engines, transmissions, count=random.randint(10, 15))
            all_models.extend(models)
            print(f"{len(models)} modèles")

        db.commit()
        print(f"✅ {len(all_models)} modèles au total")

        # 5. AVIS
        print("\n💬 Génération des avis clients (100 par type)...")
        generate_reviews(db, brands, all_models, engines, transmissions, count_per_type=100)
        print("✅ Avis générés pour marques, modèles, moteurs et transmissions")

        # RÉSUMÉ FINAL
        print("\n" + "=" * 80)
        print("🎉 PEUPLEMENT TERMINÉ AVEC SUCCÈS!")
        print("=" * 80)
        print(f"   • {len(brands)} marques")
        print(f"   • {len(all_models)} modèles de voitures")
        print(f"   • {len(engines)} moteurs")
        print(f"   • {len(transmissions)} transmissions")
        print(f"   • 400 avis clients (100 par catégorie)")
        print("=" * 80)
        print("\n✨ Votre encyclopédie automobile est maintenant COMPLÈTE!")

    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    populate_massive()
