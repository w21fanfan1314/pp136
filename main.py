from app import run

from pp136 import home_page
from pp136 import page
from pp136 import page_detail

pp136_run = run(home_page, page, page_detail)
pp136_run.get_all_res()