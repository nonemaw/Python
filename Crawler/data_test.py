
from threadpool import *
from fetch import *
from parse import *
from save import *
from config import *
import json
import urllib.parse

# # NBA球员索引URL
# url_player_index = "http://stats.nba.com/stats/commonallplayers?IsOnlyCurrentSeason=1&LeagueID=00&Season=2016-17"
#
# # NBA球员统计数据URL,传递参数PlayerID和PerMode ("PerGame", "Totals")
# url_player_stats = "http://stats.nba.com/stats/playercareerstats?LeagueID=00&PlayerID={}&PerMode={}"
#
#
# class NBAParser(Parser):
#     def html_parser(self, priority, url, keys, deep, critical, parse_repeat, content):
#         url_list, saver_list = [], []
#         if keys[0] == "index":  # 解析索引页
#             content_json = json.loads(content[-1])
#             for player in content_json["resultSets"][0]["rowSet"]:  # 解析所有球员
#                 url_list.append((url_player_stats.format((player[0], "Totals")), ("Totals", player[2]), True, 0))
#                 url_list.append((url_player_stats.format((player[0], "PerGame")), ("PerGame", player[2]), True, 0))
#
#         else:  # 解析球员数据页
#             content_json = json.loads(content[-1])
#             saver_list = content_json["resultSets"][0]["rowSet"]  # 解析球员数据
#
#         return 1, url_list, saver_list
#
#
# class NBASaver(Saver):
#     def __init__(self, file_name_total, file_name_pergame):
#         """
#         重写构造函数，添加额外表头，并且不同的源数据写到不同的目的文件
#         """
#         Saver.__init__(self)
#
#         # 写入表头
#         self.F_t = open(file_name_total, "w", encoding='utf-8')
#         self.F_t.write("\t".join(["PLAYER_NAME", "PLAYER_ID", "SEASON_ID", "LEAGUE_ID", "TEAM_ID", "TEAM_ABBREVIATION",
#                                   "GP", "GS", "MIN", "FGM", "FGA", "FG_PCT", "FG3M", "FG3A", "FG3_PCT", "FTM", "FTA",
#                                   "OREB", "DREB", "REB", "AST", "STL", "BLK", "TOV", "PF", "PTS"]) + "\n")
#         self.F_p = open(file_name_pergame, "w", encoding='utf-8')
#         self.F_p.write("\t".join(["PLAYER_NAME", "PLAYER_ID", "SEASON_ID", "LEAGUE_ID", "TEAM_ID", "TEAM_ABBREVIATION",
#                                   "GP", "GS", "MIN", "FGM", "FGA", "FG_PCT", "FG3M", "FG3A", "FG3_PCT", "FTM", "FTA",
#                                   "OREB", "DREB", "REB", "AST", "STL", "BLK", "TOV", "PF", "PTS"]) + "\n")
#
#     def item_save(self, url, keys, item):
#         if keys[0] == "Totals":
#             self.F_t.write("\t".join([keys[1]] + [str(i) for i in item]) + "\n")
#         elif keys[0] == "PerGame":
#             self.F_p.write("\t".join([keys[1]] + [str(i) for i in item]) + "\n")
#         else:
#             return False
#         return True


if __name__ == "__main__":
    # fetcher = Fetcher(max_repeat=3, sleep_time=0)
    # parser = NBAParser(max_deep=-1)
    # saver = NBASaver(file_name_total="nba_total.txt", file_name_pergame="nba_pergame.txt")
    #
    # nba_spider = ThreadPool(fetcher, parser, saver, url_filter=None)
    # nba_spider.run(url_player_index, ("index",), priority=0, deep=0, fetcher_num=10)
    #
    # exit()
    url = "https://www.jetbrains.com/help/pycharm/commenting-and-uncommenting-blocks-of-code.html"
    fetcher = Fetcher()
    parser = Parser(max_deep=0)
    saver = Saver()

    spider = ThreadPool(fetcher, parser, saver, url_filter=None)
    spider.run(url, None, priority=0, deep=0, fetcher_num=10)











