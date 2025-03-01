CREATE TABLE Users(
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(40) UNIQUE,
    role VARCHAR(40),
    hash TEXT
);

CREATE TABLE Clients(
    client_id INT,
    task_id INT,
    FOREIGN KEY (client_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (task_id) REFERENCES Tasks(task_id) ON DELETE CASCADE
);

CREATE TABLE Execs(
    exec_id INT,
    task_id INT,
    FOREIGN KEY (exec_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (task_id) REFERENCES Tasks(task_id) ON DELETE CASCADE
);


CREATE TABLE Tasks(
    task_id SERIAL PRIMARY KEY,
    task_name varchar(40),
    task_text TEXT,
    creator_id INT,
    FOREIGN KEY (creator_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

CREATE TABLE task_logs (
    log_id SERIAL PRIMARY KEY,
    act VARCHAR(40) NOT NULL,
    task_id INTEGER NOT NULL,
    action_time TIMESTAMP NOT NULL
);

CREATE OR REPLACE FUNCTION record_task()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO task_logs(act, task_id, action_time)
        VALUES ('add', NEW.task_id, NOW());
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO task_logs(act, task_id, action_time)
        VALUES ('add', OLD.task_id, NOW());
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER task_trigger
AFTER INSERT OR DELETE ON Tasks
FOR EACH ROW
EXECUTE FUNCTION record_task();


CREATE TABLE Bids(
    bid_id SERIAL PRIMARY KEY,
    task_id INT,
    exec_id INT,
    price INT,
    status VARCHAR(50),
    FOREIGN KEY (task_id) REFERENCES Tasks(task_id) ON DELETE CASCADE,
    FOREIGN KEY (exec_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

CREATE TABLE User_actions(
    user_id INT,
    task_id INT,
    user_action VARCHAR(50),
    action_time TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE SET NULL,
    FOREIGN KEY (task_id) REFERENCES Tasks(task_id) ON DELETE SET NULL
);

CREATE TABLE Task_status(
    task_id INT,
    status VARCHAR(50),
    FOREIGN KEY (task_id) REFERENCES Tasks(task_id) ON DELETE CASCADE
);