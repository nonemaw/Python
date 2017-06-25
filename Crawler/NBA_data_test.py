import spider
import json
import urllib

# NBA球员索引URL
url_player_index = "http://stats.nba.com/stats/commonallplayers?IsOnlyCurrentSeason=1&LeagueID=00&Season=2016-17"

# NBA球员统计数据URL,传递参数PlayerID和PerMode("PerGame", "Totals")
url_player_stats = "http://stats.nba.com/stats/playercareerstats?LeagueID=00&PlayerID=%s&PerMode=%s"

class NBAFetcher(spider.Fetcher):
    """
    抓取／解析以及存储球员数据，继承Fetcher／Parser／Saver类
    """
    def url_fetch(self, url, keys, critical, getch_repeat):
        """
        重写url_fetch函数
        构建Header -> 请求URL -> 获取Response -> 返回内容
        """
        headers = spider.make_headers(user_agent='all', accept_encoding='gzip')
        response = self.opener.urlopen(urllib.request.Request(url, headers=headers), timeout=10)

        content = (spider.get_html_content(response, charset='utf-8'), )
        return 1, content


class NBAParser(spider.Parser):
    def html_parser(self, priority, url, keys, deep, critical, parse_repeat, content):
        """
        重写解析过程
        由于URL的返回内容都是JSON格式，所以解析只需将字符串变为JSON然后获取JSON内容即可
        生成URL时写入不同的key来确保URL能够被正确解析
        """
        url_list, server_list = [], []
        if keys[0] == "index":  # 解析索引页
            content_json = json.loads(content[0])
            for player in content_json["resultSets"][0]["rowSet"]:  # 解析所有球员
                url_list.append((url_player_stats % (player[0], "Totals"), ("Totals", player[2]), True, 0))
                url_list.append((url_player_stats % (player[0], "PerGame"), ("PerGame", player[2]), True, 0))

        else:  # 解析球员数据页
            content_json = json.loads(content[0])
            saver_list = content_json["resultSets"][0]["rowSet"]  # 解析球员数据

        return 1, url_list, saver_list


class NBASaver(spider.Saver):
    def __init__(self, file_name_total, file_name_pergame):
        """
        重写构造函数，添加额外表头，并且不同的源数据写到不同的目的文件
        """
        spider.Saver.__init__(self)

        # 写入表头
        self.save_pipe_total = open(file_name_total, "w", encoding='utf-8')
        self.save_pipe_total.write("\t".join(["PLAYER_NAME", "PLAYER_ID", "SEASON_ID", "LEAGUE_ID", "TEAM_ID", "TEAM_ABBREVIATION",
                                              "GP", "GS", "MIN", "FGM", "FGA", "FG_PCT", "FG3M", "FG3A", "FG3_PCT", "FTM", "FTA",
                                              "OREB", "DREB", "REB", "AST", "STL", "BLK", "TOV", "PF", "PTS"]) + "\n")
        self.save_pip_pergame = open(file_name_pergame, "w", encoding='utf-8')
        self.save_pip_pergame.write("\t".join(["PLAYER_NAME", "PLAYER_ID", "SEASON_ID", "LEAGUE_ID", "TEAM_ID", "TEAM_ABBREVIATION",
                                               "GP", "GS", "MIN", "FGM", "FGA", "FG_PCT", "FG3M", "FG3A", "FG3_PCT", "FTM", "FTA",
                                               "OREB", "DREB", "REB", "AST", "STL", "BLK", "TOV", "PF", "PTS"]) + "\n")

    def item_save(self, url, keys, item):
        if keys[0] == "Totals":
            self.save_pipe_total.write("\t".join([keys[1]] + [str(i) for i in item]) + "\n")
        elif keys[0] == "PerGame":
            self.save_pip_pergame.write("\t".join([keys[1]] + [str(i) for i in item]) + "\n")
        else:
            return False
        return True


if __name__ == "__main__":
    fetcher = NBAFetcher(max_repeat=3, sleep_time=0)
    parser = NBAParser(max_deep=-1)
    saver = NBASaver(file_name_total="nba_total.txt", file_name_pergame="nba_pergame.txt")

    nba_spider = spider.WebSpider(fetcher, parser, saver, url_filter=None)
    nba_spider.set_start_url(url_player_index, ("index",))

    # 启动10个线程
    nba_spider.start_work_and_wait_done(fetcher_num=10, is_over=True)

    exit()











