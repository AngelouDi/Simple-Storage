CREATE TABLE IF NOT EXISTS storage
(
    storagename VARCHAR NOT NULL,
    PRIMARY KEY (storagename)
);

CREATE TABLE IF NOT EXISTS warehouse
(
    storagename VARCHAR NOT NULL,
    location VARCHAR NOT NULL,
    PRIMARY KEY (storagename),
    FOREIGN KEY (storagename) REFERENCES storage (storagename) ON UPDATE CASCADE ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS person
(
    username VARCHAR NOT NULL,
    pass BYTEA NOT NULL,
    email VARCHAR  NOT NULL,
    phone VARCHAR(10)  NOT NULL,
    name VARCHAR NOT NULL,
    surname VARCHAR NOT NULL,
    PRIMARY KEY (email, username),
    FOREIGN KEY (username) REFERENCES storage (storagename)
);

CREATE TABLE IF NOT EXISTS item
(
    itemname VARCHAR NOT NULL,
    id SERIAL,
    PRIMARY KEY (id),
    UNIQUE (itemname)
);

CREATE TABLE IF NOT EXISTS has
(
    storagename VARCHAR NOT NULL,
    id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity >= 0),
    ownership_date DATE DEFAULT CURRENT_DATE,
    PRIMARY KEY (storagename, id),
    FOREIGN KEY (id) REFERENCES item (id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (storagename) REFERENCES storage (storagename) ON UPDATE CASCADE ON DELETE CASCADE
);


CREATE OR REPLACE FUNCTION new_account()
    RETURNS trigger
    LANGUAGE 'plpgsql'
AS $BODY$
BEGIN

    IF new.username IS NULL THEN
        RAISE EXCEPTION 'username cannot be null';
    END IF;

    IF new.pass IS NULL THEN
        RAISE EXCEPTION 'pass cannot be null';
    END IF;

    IF new.email IS NULL THEN
        RAISE EXCEPTION 'email cannot be null';
    END IF;

    IF new.name IS NULL THEN
        RAISE EXCEPTION 'name cannot be null';
    END IF;

    IF new.surname IS NULL THEN
        RAISE EXCEPTION 'surname cannot be null';
    END IF;

    IF new.phone IS NULL THEN
        RAISE EXCEPTION 'phone cannot be null';
    END IF;

    IF EXISTS (SELECT * FROM storage WHERE storagename = new.username) THEN
        RAISE EXCEPTION 'username already in use';
    END IF;

    IF EXISTS (SELECT * FROM person WHERE email = new.email) THEN
        RAISE EXCEPTION 'email alredy in use';
    END IF;

    INSERT INTO storage VALUES (new.username);

    RETURN NEW;
    END;
$BODY$;


CREATE TRIGGER new_account
    BEFORE INSERT
    ON person
    FOR EACH ROW
    EXECUTE FUNCTION new_account();



CREATE OR REPLACE FUNCTION quantity_changed()
    RETURNS trigger
    LANGUAGE 'plpgsql'
AS $BODY$
BEGIN
    IF NEW.quantity < 0 THEN
        RAISE EXCEPTION 'Something went wrong';
        RETURN NULL;
    END IF;

    IF NEW.quantity = 0 THEN
        DELETE FROM has WHERE (storagename, id) = (NEW.storagename, NEW.id);
        RETURN NULL;
    END IF;
    RETURN NEW;

    END;
$BODY$;

CREATE TRIGGER quantity_changed
BEFORE UPDATE
ON has FOR EACH ROW
EXECUTE FUNCTION quantity_changed();

CREATE OR REPLACE FUNCTION transfer_possession(new_owner VARCHAR, old_owner VARCHAR, item_id INT, req_quantity INT)
RETURNS VOID
AS $$
BEGIN
    IF EXISTS (SELECT quantity FROM has WHERE
     id = item_id AND
     storagename = old_owner AND
     req_quantity <= quantity) THEN
     UPDATE has SET quantity = quantity - req_quantity WHERE
     id = item_id AND storagename = old_owner;
   ELSE RAISE EXCEPTION 'Requested more than existing.';
   END IF;

   IF exists (SELECT id FROM has WHERE
       id = item_id AND
       storagename = new_owner) THEN
       UPDATE has SET quantity = quantity + req_quantity WHERE
       id = item_id AND storagename = new_owner;
   ELSE INSERT INTO has VALUES (new_owner, item_id, req_quantity);
   END IF;

END;
$$
LANGUAGE 'plpgsql';

CREATE OR REPLACE FUNCTION add_new_ownership(new_owner VARCHAR, new_itemname VARCHAR, new_quantity INT)
RETURNS VOID
AS $$
DECLARE
    item_id INT;
BEGIN
    -- TODO: must check if user exists etc?
    IF NOT EXISTS (SELECT id FROM item WHERE
                   LOWER(itemname) = LOWER(new_itemname)) THEN
                   INSERT INTO item VALUES (new_itemname);
    END IF;

   item_id := (SELECT id FROM item WHERE
   itemname = new_itemname);

    IF EXISTS (SELECT id FROM has WHERE
              id = item_id AND
              storagename = new_owner) THEN
              UPDATE has SET quantity = quantity + new_quantity WHERE
              id = item_id AND
              storagename = new_owner;
    ELSE INSERT INTO has VALUES (new_owner, item_id, new_quantity);
    END IF;
END;
$$
LANGUAGE 'plpgsql';

CREATE OR REPLACE FUNCTION new_warehouse()
    RETURNS trigger
AS $$
BEGIN

    IF new.storagename IS NULL THEN
        RAISE EXCEPTION 'Warehouse name cannot be null';
    END IF;

    IF new.location IS NULL THEN
        RAISE EXCEPTION 'Location cannot be null';
    END IF;

    IF EXISTS (SELECT * FROM storage WHERE storagename = new.storagename) THEN
        RAISE EXCEPTION 'Warehouse already exists';
    END IF;

    INSERT INTO storage VALUES (new.storagename);

    RETURN NEW;
    END;
$$ LANGUAGE 'plpgsql';

CREATE TRIGGER new_warehouse
    BEFORE INSERT
    ON warehouse
    FOR EACH ROW
    EXECUTE FUNCTION new_warehouse();

