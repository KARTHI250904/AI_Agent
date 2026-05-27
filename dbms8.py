import mysql.connector
import time


def test_replication():
    try:
        # Master (WRITE)
        master_config = {
            'host': '127.0.0.1',
            'port': 3306,
            'user': 'root',
            'password': 'root',
            'database': 'lab'
        }

        # Slave (READ)
        slave_config = {
            'host': '127.0.0.1',
            'port': 3307,
            'user': 'root',
            'password': 'root',
            'database': 'lab'
        }

        # Connect to master
        master = mysql.connector.connect(**master_config)
        m_cursor = master.cursor()

        print("Inserting into MASTER...")
        m_cursor.execute(
            "INSERT INTO college (college_id, name, city) VALUES (%s, %s, %s)",
            (101, "ABC College", "Chennai")
        )
        master.commit()

        print("Waiting for replication...")
        time.sleep(3)

        # Connect to slave
        slave = mysql.connector.connect(**slave_config)
        s_cursor = slave.cursor()

        print("Reading from SLAVE...")
        s_cursor.execute(
            "SELECT * FROM college ORDER BY college_id DESC LIMIT 1"
        )
        result = s_cursor.fetchone()

        if result:
            print(f"✔ Replicated Data: ID={result[0]}, Name={result[1]}, City={result[2]}")
        else:
            print("❌ No data found on slave")

    except mysql.connector.Error as err:
        print("Error:", err)

    finally:
        if 'm_cursor' in locals(): m_cursor.close()
        if 's_cursor' in locals(): s_cursor.close()
        if 'master' in locals(): master.close()
        if 'slave' in locals(): slave.close()


test_replication()
