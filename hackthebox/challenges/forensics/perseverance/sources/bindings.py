import logging

from cim import CIM
from cim.objects import Namespace

logging.basicConfig(level=logging.ERROR)

c = CIM('win7', './Repository/')
with Namespace(c, "root\\subscription") as ns:
    for binding in ns.class_("__filtertoconsumerbinding").instances:
        print("binding: ", binding)
        filterref = binding.properties["Filter"].value
        consumerref = binding.properties["Consumer"].value
        filter = ns.get(ns.parse_object_path(filterref))
        consumer = ns.get(ns.parse_object_path(consumerref))

        print("  filter: ", filter)
        try:
            print("    language: ", filter.properties["QueryLanguage"].value)
            print("    query: ", filter.properties["Query"].value)
        except IndexError:
            print("    not found.")


        print("  consumer: ", consumer)
        try:
            if "CommandLineTemplate" in consumer.properties:
                print("    payload: ", consumer.properties["CommandLineTemplate"].value)
        except IndexError:
            print("    not found.")
