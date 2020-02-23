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


if __name__ == "__main__":
    machines = vultr_scraper()

    if "--print" in sys.argv:
        Machine.print_list(machines)
