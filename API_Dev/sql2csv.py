import csv
import re

# 打开SQL文件
with open('air_conditioner_backup.sql', 'r') as file:
    sql_data = file.read()

# 匹配INSERT语句中的值
matches = re.findall(r"INSERT INTO `.*?` VALUES \((.*?)\);", sql_data)

# 打开CSV文件进行写入
with open('output.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)

    for match in matches:
        # 分割每个值并移除多余的引号
        row = [x.strip("'") for x in match.split(",")]
        writer.writerow(row)

print("Data successfully written to output.csv")


