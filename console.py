#!/usr/bin/python3
"""module that houses the console"""

import cmd
from models.base_model import BaseModel
from models import storage
import json
import shlex
from datetime import datetime
import re
from models.user import User
from models.state import State
from models.city import City
from models.amenity import Amenity
from models.place import Place
from models.review import Review


class HBNBCommand(cmd.Cmd):
    """this is the console using the Cmd module"""
    prompt = "(hbnb) "
    my_classes = {
        "BaseModel": BaseModel,
        "User": User,
        "State": State,
        "City": City,
        "Amenity": Amenity,
        "Place": Place,
        "Review": Review
    }

    def check_arg_validity_classes(self, args):
        """checks if the class is a real class and that it was given in args"""
        if len(args) < 1 or args[0] == '':
            print("** class name missing **")
            return True
        elif args[0] not in self.my_classes:
            print("** class doesn't exist **")
            return True
        return False

    def check_arg_validity_classes_ids(self, args):
        """checks all as previous with extra check for id"""
        if self.check_arg_validity_classes(args):
            return True
        elif len(args) < 2:
            print("** instance id missing **")
            return True
        else:
            search_key = '.'.join(args[:2])
            search_result = storage.search(search_key)
            if search_result is False:
                print("** no instance found **")
                return True
        return search_key

    def check_arg_validity_classes_attributes(self, args):
        """checks all as previous with extra check for attributes as dict"""
        search_key = self.check_arg_validity_classes_ids(args)
        args_search = ["id", "created_at", "updated_at"]
        if search_key is True:
            return True
        elif len(args) < 3:
            print("** attribute name missing **")
            return True
        elif len(args) < 4:
            print("** value missing **")
            return True
        elif args[2] in args_search:
            return True
        return search_key

    def onecmd(self, line):
        """implement spcific commands"""
        arguments = line.split(".")
        if arguments[0] in self.my_classes and len(arguments) > 1:
            if arguments[1] == "all()":
                self.do_all(arguments[0])
            elif arguments[1] == "count()":
                print(storage.count_class(arguments[0]))
            elif arguments[1].startswith("show"):
                id = self.extract_id(arguments[0], arguments[1])
                if id is not False:
                    self.do_show(f"{arguments[0]} {id}")
            elif arguments[1].startswith("destroy"):
                id = self.extract_id(arguments[0], arguments[1])
                if id is not False:
                    self.do_destroy(f"{arguments[0]} {id}")
            elif arguments[1].startswith("update"):
                id = self.extract_id(arguments[0], arguments[1])
                if id is not False:
                    self.update(arguments[0], arguments[1], id)
            else:
                return super().onecmd(line)

        else:
            return super().onecmd(line)

    def extract_id(self, class_name, line):
        """extract class id"""
        id_rgx = re.search(r"(\w{0,8}-\w{0,4}-\w{0,4}-\w{0,4}-\w{0,12})", line)
        try:
            id = id_rgx.group(0)
        except Exception:
            print("** no instance found **")
            return False
        if len(id) == 36:
            search_key = f"{class_name}.{id}"
            search_result = storage.search(search_key)
            if search_result is False:
                print("** no instance found **")
                return False
            else:
                return id
        else:
            print("** no instance found **")
            return False

    def update(self, class_name, line, id):
        """update values"""
        array = line.split(", ")
        if array[1].startswith("{"):
            dictionary_string = line.split(", ", 1)[1][:-1]
            dictionary_string = dictionary_string.replace("'", "\"")
            dictionary = json.loads(dictionary_string)
            self.update_dictionary(dictionary, class_name, id)
        elif len(array) >= 3:
            key = array[1].replace("\"", "")
            value = array[2].replace("\"", "")
            value = value.replace(")", "")
            self.do_update(f"{class_name} {id} {key} {value}")
        elif len(array) == 2:
            print("** value missing **")
        else:
            print("** attribute name missing **")

    def update_dictionary(self, dictionary, class_name, id):
        """updates values based on dictionary"""
        for key, value in dictionary.items():
            self.do_update(f"{class_name} {id} {key} {value}")

    def do_quit(self, line):
        """quits the program"""
        return True

    def do_create(self, line):
        """creates a class instance"""
        args = line.split(" ")
        if self.check_arg_validity_classes(args):
            pass
        else:
            created_class = self.my_classes[line]()
            print(created_class.id)
            storage.new(created_class)
            storage.save()

    def do_show(self, line):
        """shows an instance given a classname and id"""
        args = line.split(" ")
        search_key = self.check_arg_validity_classes_ids(args)
        if search_key is not True:
            search_result = storage.search(search_key)
            print(search_result)

    def do_destroy(self, line):
        """destroys a class give classname and id"""
        args = line.split(" ")
        search_key = self.check_arg_validity_classes_ids(args)
        if search_key is not True:
            storage.destroy(search_key)

    def do_all(self, line):
        """shows all of a certain class or all classes if no extra arg"""
        args = line.split(" ")
        if args[0] == "" or self.check_arg_validity_classes(args) is False:
            result = storage.get_all_of_class(args[0])
            print(result)

    def do_update(self, line):
        """updates the class args[0] with the variable args[1]"""
        args = shlex.split(line)
        search_key = self.check_arg_validity_classes_attributes(args)
        if search_key is not True:
            search_instance = storage.search(search_key)
            setattr(search_instance, args[2], args[3])
            storage.save()

    def do_EOF(self, line):
        """quits the program"""
        return True

    def emptyline(self):
        """does nothing"""
        pass


if __name__ == '__main__':
    """this is the initialisation of the cmdloop"""
    HBNBCommand().cmdloop()
