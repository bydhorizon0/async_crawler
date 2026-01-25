CREATE TABLE scrap_target_list(
   seq INT AUTO_INCREMENT PRIMARY KEY,
   type ENUM('PAGE', 'API') NOT NULL,
   site_url VARCHAR(500) NOT NULL,
   site_name VARCHAR(100),
   category VARCHAR(50),
   detail_url_format VARCHAR(500) NOT NULL
       COMMENT 'ex) /view.do?seq={id}',
   list_path VARCHAR(255) NOT NULL
       COMMENT 'list XPath',
   id_path VARCHAR(255) NOT
       NULL COMMENT 'id XPath',
   id_attr VARCHAR(50)
       COMMENT 'href | data-id | ...',
   id_regex VARCHAR(255)
       COMMENT 'id regex',
   title_path VARCHAR(255)
       NOT NULL COMMENT 'title XPath',
   description VARCHAR(255),
   created DATETIME DEFAULT CURRENT_TIMESTAMP,
   updated DATETIME DEFAULT CURRENT_TIMESTAMP
       ON UPDATE CURRENT_TIMESTAMP
);

/*
- 페이지당 대기 시간은 랜덤으로 주는게 좋을 거 같음
- 크롤링 실패 로그 테이블
- 사이트 깨졌을 때 자동 감지 (매일 아침 알림?)
*/

CREATE TABLE scrap_save (
   seq INT AUTO_INCREMENT PRIMARY KEY,
   detail_url VARCHAR(255) NOT NULL,
   title VARCHAR(255) NOT NULL,
   category VARCHAR(50),
   target_seq INT NOT NULL,
   is_active TINYINT DEFAULT 1 COMMENT '게시물 활성화',
   created DATETIME DEFAULT CURRENT_TIMESTAMP,
   updated DATETIME DEFAULT CURRENT_TIMESTAMP
               ON UPDATE CURRENT_TIMESTAMP,
   CONSTRAINT fk_scrap_save_target
       FOREIGN KEY (target_seq)
       REFERENCES scrap_target_list(seq)
       ON DELETE CASCADE
       ON UPDATE CASCADE
);