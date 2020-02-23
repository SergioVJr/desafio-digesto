from __future__ import annotations  # From 4.0, allows a method to reference its own class in type hint
import sys
import requests
from lxml import html
import json
import csv
from typing import List


class Machine:
    cpu: str
    memory: str
    storage: str
    bandwidth: str
    price: str

    @staticmethod
    def print_list(m_list: List[Machine]) -> None:
        """Format and print a list of Machines to the console"""
        format_str = "{:<10}{:<9}{:<9}{:<11}{}"
        print(format_str.format("CPU/vCPU", "Memory", "SSD", "Bandwidth", "Price"))
        for m in m_list:
            print(format_str.format(m.cpu, m.memory, m.storage, m.bandwidth, m.price))

    @staticmethod
    def save_json(m_list: List[Machine]) -> None:
        """Store a list of Machines as a JSON file"""
        with open("machines.json", 'w') as file:
            json_str = json.dumps([m.__dict__ for m in m_list])
            file.write(json_str)

    @staticmethod
    def save_csv(m_list: List[Machine]) -> None:
        """Store a list of Machines as a CSV file"""
        with open("machines.csv", 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=["cpu", "memory", "storage", "bandwidth", "price"])
            writer.writerow({"cpu": "CPU/vCPU",
                             "memory": "Memory",
                             "storage": "SSD",
                             "bandwidth": "Bandwidth",
                             "price": "Price"})
            for m in m_list:
                writer.writerow(m.__dict__)


def vultr_scraper() -> List[Machine]:
    """Obtain a list of cloud machines from https://www.vultr.com/pricing/"""
    page = requests.get("https://www.vultr.com/pricing/")
    tree = html.fromstring(page.content)

    # Extract the rows from the pricing table
    rows = tree.xpath('//div[@id="compute"]//div[@class="pt__row-content"]')

    m_list = []
    for row in rows:
        m = Machine()
        columns = row.xpath('./div[contains(@class,"pt__cell")]')
        m.storage = columns[1][0][0].text
        m.cpu = columns[2][0][0].text
        m.memory = columns[3][0].text
        m.bandwidth = columns[4][0][0].text
        m.price = columns[5][0][0].text + columns[5][0][0].tail.strip("\n\t")
        m_list.append(m)

    return m_list


def digitalocean_scraper() -> List[Machine]:
    """Obtain a list of cloud machines from https://www.digitalocean.com/pricing/"""
    page = requests.get("https://www.digitalocean.com/pricing/")
    tree = html.fromstring(page.content)

    # Extract the rows from the pricing table
    rows = tree.xpath('//div[@id="standard-droplets-pricing-table"]//table[@class="www-Table PricingTable"]/tbody/tr')

    m_list = []
    for row in rows:
        m = Machine()
        columns = row.xpath('.//td')
        m.memory = columns[0][0].text.strip()
        m.cpu = columns[1].text.strip()
        m.bandwidth = columns[2].text.strip()
        m.storage = columns[3].text.strip().replace(',', '')
        m.price = columns[4][0].text.strip()
        m_list.append(m)

    return m_list


if __name__ == "__main__":
    machines = vultr_scraper()
    machines.extend(digitalocean_scraper())

    if "--print" in sys.argv:
        Machine.print_list(machines)
    if "--save_json" in sys.argv:
        Machine.save_json(machines)
    if "--save_csv" in sys.argv:
        Machine.save_csv(machines)
