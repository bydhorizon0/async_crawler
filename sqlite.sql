/*
 - 페이지당 대기 시간은 랜덤으로 주는게 좋을 거 같음
 - 크롤링 실패 로그 테이블
 - 사이트 깨졌을 때 자동 감지 (매일 아침 알림?)\
*/
CREATE TABLE scrap_targets(
   seq INTEGER PRIMARY KEY AUTOINCREMENT,
   type TEXT NOT NULL CHECK (type IN ('PAGE', 'API')) DEFAULT 'PAGE',
   pagination_path TEXT,
   site_url TEXT NOT NULL,
   site_name TEXT,
   category TEXT,
   detail_url_format TEXT NOT NULL, -- 'ex) /view.do?seq={id}'
   list_path TEXT NOT NULL, -- 'list XPath'
   id_path TEXT NOT NULL, -- 'id XPath'
   id_attr TEXT, -- 'href | data-id | ...'
   id_regex TEXT, -- 'id regex'
   title_path TEXT NOT NULL, -- 'title XPath'
   description TEXT,
   created DATETIME DEFAULT CURRENT_TIMESTAMP,
   updated DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 업데이트시 트리거로 업데이트 시간('updated') 자동 업데이트
CREATE TRIGGER trg_scrap_targets_updated
    AFTER UPDATE ON scrap_targets
    FOR EACH ROW
    BEGIN
        UPDATE scrap_targets SET updated = CURRENT_TIMESTAMP WHERE seq = OLD.seq;
    END;

INSERT INTO scrap_targets (site_url, site_name, category, detail_url_format, list_path, id_path, id_attr, id_regex, title_path)
VALUES (
        'https://www.seoul.go.kr/news/news_notice.do?bbsNo=277&curPage={}',
        '서울특별시',
        '고시공고',
        'https://www.seoul.go.kr/news/news_notice.do?bbsNo=277&nttNo={}',
        '//*[@id="seoul-integrated-board"]/table/tbody/tr',
        '//td[2]/a',
        'href',
        'fnTbbsView\(''(\d+)''\)',
        '//td[2]/a'
       );

INSERT INTO scrap_targets (site_url, site_name, category, detail_url_format, list_path, id_path, id_attr, id_regex, title_path)
VALUES (
    'https://www.busan.go.kr/nbgosi?curPage={}',
    '부산광역시',
    '고시공고',
    'https://www.busan.go.kr/nbgosi/view?gosiGbn=A&sno={}',
    '//*[@id="contents"]/div[2]/table/tbody/tr',
    '//td[2]/a',
    'href',
    'sno=(\d+)&',
    '//td[2]/a'
);

INSERT INTO scrap_targets (site_url, site_name, category, detail_url_format, list_path, id_path, id_attr, id_regex, title_path)
VALUES (
    'https://ulsan.go.kr/u/rep/transfer/notice/list.ulsan?mId=001004002000000000&srchGubun=A&srchType=srchSj&curPage={}',
    '울산광역시',
    '고시공고',
    'https://ulsan.go.kr/u/rep/transfer/notice/{}.ulsan?mId=001004002000000000&gosiGbn=A',
    '//*[@id="contents_inner"]/div[3]/table/tbody/tr',
    '//td[2]/a',
    'href',
    '.\/(\d+).ulsan',
    '//td[2]/a'
);

INSERT INTO scrap_targets (pagination_path, site_url, site_name, category, detail_url_format, list_path, id_path, id_attr, title_path)
VALUES (
    '//*[@id="app"]/div[4]/div/ul/li/a',
    'https://www.jeju.go.kr/news/news/law/jeju2.htm',
    '제주특별자치도',
    '고시공고',
    'https://www.jeju.go.kr/news/news/law/jeju2.htm{}',
    '//*[@id="gosiBody"]/tr',
    '//td[3]/a',
    'href',
    '//td[3]/a'
);

INSERT INTO scrap_targets (site_url, site_name, category, detail_url_format, list_path, id_path, id_attr, id_regex, title_path)
VALUES (
    'https://www.bizinfo.go.kr/sii/siia/selectSIIA200View.do?rows=15&cpage={}',
    '기업마당',
    '지원사업',
    'https://www.bizinfo.go.kr/sii/siia/selectSIIA200Detail.do?schEndAt=N&pblancId={}',
    '//*[@id="articleSearchForm"]/div[2]/div[4]/table/tbody/tr',
    '//td[3]/a',
    'href',
    'pblancId=(PBLN_\d+)',
    '//td[3]/a'
);

INSERT INTO scrap_targets (site_url, site_name, category, detail_url_format, list_path, id_path, id_attr, id_regex, title_path)
VALUES (
    'https://www.bizinfo.go.kr/sii/siia/selectSIIA200View.do?rows=15&cpage={}',
    '기업마당',
    '지원사업',
    'https://www.bizinfo.go.kr/sii/siia/selectSIIA200Detail.do?schEndAt=N&pblancId={}',
    '//*[@id="articleSearchForm"]/div[2]/div[4]/table/tbody/tr',
    '//td[3]/a',
    'href',
    'pblancId=(PBLN_\d+)',
    '//td[3]/a'
);

INSERT INTO scrap_targets (site_url, site_name, category, detail_url_format, list_path, id_path, id_attr, id_regex, title_path)
VALUES (
    'https://www.k-startup.go.kr/web/contents/bizpbanc-ongoing.do?page={}',
    '창업넷',
    '사업공고',
    'https://www.k-startup.go.kr/web/contents/bizpbanc-ongoing.do?pbancClssCd=PBC010&schM=view&pbancSn={}',
    '//*[@id="bizPbancList"]/ul/li',
    '//div/div[1]/div[2]/a',
    'href',
    'go_view\((\d+)\)',
    '//div/div[1]/div[2]/a'
);

/*

 */
CREATE TABLE scrap_result (
   seq INTEGER PRIMARY KEY AUTOINCREMENT,
   detail_url TEXT NOT NULL,
   title TEXT NOT NULL,
   category TEXT,
   target_seq INTEGER NOT NULL,
   is_active INTEGER DEFAULT 1, -- '게시물 활성화'
   created DATETIME DEFAULT CURRENT_TIMESTAMP,
   CONSTRAINT fk_scrap_save_target
       FOREIGN KEY (target_seq)
       REFERENCES scrap_target_list(seq)
       ON DELETE CASCADE
       ON UPDATE CASCADE
);

-- 업데이트시 트리거로 업데이트 시간('updated') 자동 업데이트
CREATE TRIGGER trg_scrap_result_updated
    AFTER UPDATE ON scrap_result
    FOR EACH ROW
    BEGIN
        UPDATE scrap_result SET updated = CURRENT_TIMESTAMP WHERE seq = OLD.seq;
    END;