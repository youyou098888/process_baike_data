# coding=utf-8
import knowledge_base
import mention_id
import jieba
import jieba.posseg as pseg
import similarity
import editdistance

__author__ = 'yuyang'

# kb = knowledge_base.KnowledgeBase()
# kb.load_knowledge_base()
# # kb.show()

# mid = mention_id.MentionID()
# mid.load_mention_2_id()
# mid.show()

for item in jieba.cut_for_search(u'学校城'):
    print type(item), item
    # token, pos = item
    # token, pos = item.word, item.flag
    # print token, pos

# 什么<体裁>吗，<A>还是<B>
# sent = u'江陵	之	战	是	哪	一	年	爆发	的'.split('\t')
# for token in sent:
#     print token
# print [x for x in jieba.cut_for_search('桃城中学是什么学校')]
sim = similarity.Similarity()
a = '吴彦祖，1974年9月30日出生于美国<a>旧金山</a>，祖籍<a>上海</a>在<a>加州</a>成长，<a>演员</a>、<a>模特</a>。 |||1997年回到<a>香港</a>，开始电影及<a>模特儿</a>工作。1998年，吴彦祖接拍第一部电影《<a>美少年之恋</a>》，由<a>杨凡</a>导演一部同性恋电影。2004年，与<a>成龙</a>主演了《<a>新警察故事</a>》，并获得了<a>金马奖</a>演员类奖项“第41届金马奖最佳男配角”。2007年凭电影《<a>四大天王</a>》，于第26届<a>香港电影金像奖</a>中夺得新晋<a>导演</a>奖。2010年4月6日，吴彦祖与相恋8年的女友<a>Lisa S</a>在<a>南非</a>举行婚礼，结为夫妻。  |||     吴彦祖杂志图片(20张)   |||吴彦祖出生于<a>加利福尼亚州</a>伯克利，并在<a>奥林达</a>扶养长大。当他看到<a>李连杰</a>主演的<a>少林寺</a>电影后，对武术产生了兴趣。11岁时，吴彦祖便拜一名北京艺人为师，擅长枪和棍。1995年时，还专程飞到北京修习武术。 |||吴彦祖在加州奥克兰海德劳斯莱斯学校上学，过后在美国俄勒冈大学攻读建筑系，1993年首次得到建筑副修奖学金。1994年，赢得California Martial Art Competitions的亚军，并在美国西岸被排名第二位。他成立了俄勒冈大学<a>中国武术</a>学会，并成为第一任教练，收了二十几个徒弟，一共教了五年。同年，随师父到北京什刹海武校参加集训，获得了北京国际武术比赛长拳组第五名，太极拳组第六名。 |||1997年毕业后，吴彦祖前往香港，在他姐姐的建议下开始当模特儿。四个月后，电影导演<a>杨凡</a>在一个地铁站里看到吴彦祖拍摄的服装广告后，与他接洽成为他下一个电影的演员。 |||     吴彦祖杂志封面照(24张)   |||1998年，吴彦祖接拍第一部电影《<a>美少年之恋</a>》，由杨凡导演一部同性恋电影。 |||1999年，由吴彦祖主演的电影《<a>紫雨风暴</a>》，荣获第19届香港电影金像奖最佳摄影，第19届香港电影金像奖最佳剪接。 |||2004年，成龙重新翻拍的《<a>新警察故事</a>》找到吴彦祖，作为第三男主角。并获得第41届<a>台湾电影金马奖</a>最佳男配角，第25届<a>中国电影金鸡奖</a>最佳男配角提名，第24届香港电影金像奖最佳男配角提名 。 |||2007年，凭电影《<a>四大天王</a>》，于第26届<a>香港电影金像奖</a>中夺得新晋<a>导演</a>奖。|||2009年，由<a>麦兆辉</a>及<a>庄文强</a>编剧及导演的电影《<a>窃听风云</a>》，在该片里首次与<a>刘青云</a>演对手戏。     吴彦祖(19张)   |||2012年，导演陆川的新作《<a>王的盛宴</a>》西楚霸王项羽一角将由吴彦祖担纲。 |||2013年，吴彦祖、冯德伦监制的年度犯罪动作大片电影《<a>控制</a>》定于11月21日上映。 |||2014年6月18日，因母亲患上重病，吴彦祖决定暂停所有娱乐圈工作。解散经纪公司Revolution Talent Management Ltd(星革盟有限公司)。 |||2014年8月12日，吴彦祖微博否认退出娱乐圈：热爱演艺工作 从没想过退出 ，并开始全面复工。由韩国导演朴赞郁执导，吴彦祖出演的微电影《孵花》，于2014年10月22日在上海时装周全球首映 。|||2014年12月20日，吴彦祖将出演AMC电视网打造的美剧版《西游记》(暂用名Badlands)男主角Sunny。'
b = '美,法,中混血儿 年龄26 身高172CM 体重117斤 三围33C,24,35 入行约5年,因与吴彦祖拍拖而被大家熟悉.每场catwalk约收＄6000，约计每月收入5至10万．．． Lisa.S，一个知名度不太高的“知名模特”，她的父亲是中法混血、母亲是犹太人，在与港星吴彦祖恋爱之前，很少有人知道这个名字。穿着一身大红色性感舞服、跳着充满野性的斗牛舞，Lisa.S也出现在《舞林大会》的舞台上。事实上，对于这个混血女友，吴彦祖的粉丝大多持  反对意见，而Lisa.S接受记者采访时，竟也一不小心流露了自己过去有些不堪的感情生活。  他像羊，非常温顺 帅气、话不多，这是吴彦祖在记者面前一贯保持的酷酷形象，没想到在女友Lisa.S面前，他却完全变了一个人。Lisa.S乐滋滋地描述着男友：“如果你要问我他做过的浪漫的事情，那么我想他每天都很浪漫，每天都让我笑个不停，实在太有趣了。” 记者追问为何在媒体面前的吴彦祖如此沉闷，Lisa.S不无得意地表示，因为吴彦祖是个很专业的演员，所以他的温柔只留在了女友面前，“我想，到了70岁，就算他已经不是很帅了，但肯定温柔如昔，仍然是个很有趣的老头。” 因为Lisa.S在《舞林大会》跳的是斗牛舞，所以记者询问生活中的吴彦祖是不是也像一头牛，她却大笑着说：“不会，不会，他像一头羊。会给我烧饭、逗我开心，非常温顺。”虽然男友如此十全十美，但Lisa.S却坦言自己并不想两人在工作上有任何合作，态度显得非常反感，“我们在《宝贝计划》中曾经合作过，但那时没有对手戏。我永远也不想和他在电影中合作，因为他实在是个优秀的演员，在他旁边，我会自卑。”Lisa.S无奈表示，其实能和她在电影中合作的男明星实在不多，因为她太高了。  我是牛，不会妒忌 许是多年在国外生活的经历铸就了她如此奔放的性格，接受记者采访时，一会儿大笑、一会儿做各种夸张的动作，实在不是一个淑女。Lisa.S自己昨天也不小心暴露了过去混乱的情史。“我有过很多坏男友，和他们在一起时我很痛苦，经常吵架、相互谩骂，生活没有一天是安宁的，直到遇到了吴彦祖，我才知道原来好男人是这样的，和他在一起后，我们从来没有吵过架。”Lisa.S透露，其实自己以前是吴彦祖的粉丝，一次偶然地在杂志封面上看到吴彦祖时，就感叹：“怎么有这么帅的男人。”直到两年后，两人一见钟情……据悉，正因为过去不堪的经历，加上与吴彦祖相差悬殊的知名度，Lisa.S对吴彦祖和其他女人的来往只能睁一只眼闭一只眼，前阵子曾有人拍到吴彦祖在沪与某女子的亲密照，记者就此向Lisa.S求证时，她强装无所谓：“我不会像其他女孩那样妒忌，我信任他。”而不断被问婚期的Lisa.S有些不耐烦地表示，自己从来没有结婚的概念，不过，为了圈住男友的心，她正考虑先生个孩子。'
c = 'Lisa.S'
print sim.similarity(a, b)
print sim.similarity(c, b)
