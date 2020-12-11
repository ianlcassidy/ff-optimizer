from roto_guru import scrape_and_save_data as rg_scrape_and_save
from football_locks import scrape_and_save_data as fl_scrape_and_save
from fantasy_pros import scrape_and_save_data as fp_scrape_and_save
from utils import what_week_is_it

if __name__ == "__main__":
    week = what_week_is_it()
    print("**** scraping Roto Guru data ***")
    rg_scrape_and_save(week)
    print("**** scraping Football Locks data ***")
    fl_scrape_and_save(week)
    print("**** scraping Fantasy Pros data ***")
    fp_scrape_and_save(week)
