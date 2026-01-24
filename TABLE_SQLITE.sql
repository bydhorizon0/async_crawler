CREATE TABLE scrap_page_list(
    seq INT AUTO_INCREMENT PRIMARY KEY,
    site_url VARCHAR(500) NOT NULL,
    site_name VARCHAR(100),
    category VARCHAR(50),
    list_path VARCHAR(255) NOT NULL,
    title_path VARCHAR(255) NOT NULL,
    detail_url_path VARCHAR(255) NOT NULL, -- 링크를 path로 수집할 수 없는 경우도 있음
    description VARCHAR(255),
    created DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated DATETIME DEFAULT CURRENT_TIMESTAMP
                ON UPDATE CURRENT_TIMESTAMP
);