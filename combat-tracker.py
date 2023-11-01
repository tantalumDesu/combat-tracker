import json, re
from random import randint

class Character:
    def __init__(self, name, ac, hp_dice=None, init_dice=None):
        self.name = name
        self.ac = ac
        self.hp_dice = hp_dice
        self.init_dice = init_dice
        self.hp = None
        self.hpmax = None
        self.initiative = None

        self.dying = False
        self.death_save_success = 0
        self.death_save_failure = 0

        self.alignment = None

        self.str = None
        self.dex = None
        self.con = None
        self.int = None
        self.wis = None
        self.cha = None

        self.conditions = []
        self.is_player = None
        self.attacks = None
        self.special = None
        self.skills = None
        self.senses = None

    def resolve_dice(self, dice_notation):
        pattern = re.compile(r'(\d+)?d(\d+)([+-]\d+)?')
        dice_expression_clean=re.sub(r"\s+", "", dice_notation)
        match = pattern.match(dice_expression_clean) 
        if match:
            num_dice_str = match.group(1)
            num_dice = int(num_dice_str) if num_dice_str else 1
            dice_faces = int(match.group(2))   
            bonus_str = match.group(3)
            bonus = int(bonus_str) if bonus_str else 0          
            total = sum(randint(1, dice_faces) for _ in range(num_dice)) + bonus
            return total
        else:
            raise ValueError("Invalid dice expression: " + dice_notation)

    def resolve_character(self):
        if self.hp is None:
            self.hp = self.resolve_dice(self.hp_dice)
        if self.initiative is None:
            self.initiative = self.resolve_dice(self.init_dice)

    def take_damage(self, damage, combat_round):
        self.hp -= damage
        if self.hp <=0 and self.is_player == False:
            input(f"\n{self.name} is dead!")
            combat_round.remove(self)
        elif self.hp <= -self.hpmax and self.is_player:
            input(f"\n{self.name} is killed instantly!")
            combat_round.remove(self)
        elif self.is_player and self.dying:
            self.death_save_failure += 1
            input(f"\n{self.name} fails a death save!")
            self.hp = 0
            if self.death_save_failure >=3:
               input(f"{self.name} is dead!")
               combat_round.remove(self) 
        elif self.hp <=0 and self.is_player:
            input(f"\n{self.name} is dying!")
            self.conditions.append("Unconscious")
            self.hp = 0
            self.dying = True

    def heal_damage(self, heal):
        self.hp += heal
        if self.hp > self.hpmax:
            self.hp = self.hpmax
        if self.hp == self.hpmax:
            print(f"\n{self.name} is fully healed.")
        if self.hp > 0:
            self.dying = False
            if "Unconscious" in self.conditions:
                self.conditions.remove("Unconscious")
            if "Stable" in self.conditions:
                self.conditions.remove("Stable")

    def death_save(self):
        save = input("Death save roll success? y/n: ").lower()
        if save == "y":
            self.death_save_success += 1
            if self.death_save_success < 3:
                crit = input("Critical? y/n: ").lower()
                if crit == "y":
                    self.death_save_success += 1
            if self.death_save_success >= 3:
                self.dying = False
                self.hp = 0
                self.death_save_failure = 0
                self.death_save_success = 0
                self.conditions.append("Stable")
                print(f"{self.name} is Stable!")
        elif save == "n":
            self.death_save_failure += 1
            if self.death_save_failure < 3:
                crit = input("Critical? y/n: ").lower()
                if crit == "y":
                    self.death_save_failure += 1
            if self.death_save_failure >= 3:
                print(f"{self.name} is dead!")
                combat_round.remove(self)
    
    def add_condition(self):
        with open("conditions.txt", "r") as file:
            conditions_list = json.load(file)
        print("\nConditions:")
        for i, condition in enumerate(conditions_list.keys(), 1):
            print(f"{i}: {condition}")
        while True:
            selected_condition_index = int(input(f"Choose a condition to add to {self.name}: ")) -1
            condition_names = list(conditions_list.keys())
            selected_condition = condition_names[selected_condition_index]
            if selected_condition in self.conditions:
                print(f"\n{self.name} is already affected by {selected_condition}.")
                break
            sure = input(f"\nAdd {selected_condition} to {self.name}? y/n: ").lower()
            if sure == "y":
                self.conditions.append(selected_condition)
                break
            else: break
        self.conditions.sort()
    
    def remove_condition(self):
        if self.conditions == []:
            print("\nNo conditions to remove")
        else:
            for i, condition in enumerate(self.conditions, 1):
                print(f"{i}: {condition}")
            selected_condition_index = int(input("Choose a condition to remove: ")) -1
            selected_condition = self.conditions[selected_condition_index]
            sure = input(f"Remove {selected_condition} from {self.name}? y/n: ").lower()
            if sure == "y":
                self.conditions.remove(selected_condition)    
        self.conditions.sort()    

    def describe_conditions(self):
        with open("conditions.txt", "r") as file:
            conditions_list = json.load(file)
        for condition in self.conditions:
            description = conditions_list.get(condition, "No such condition")
            print(f"{condition}: {description}")
        
    def display_info(self):
        print(f"\n{self.name} (HP: {self.hp}, AC: {self.ac}, Initiative: {self.initiative})")
        if self.conditions:
            conditions_str = ', '.join(self.conditions)
            print(f"Conditions: {conditions_str}")
        if self.is_player:
            print("Player character")
        else:
            print("NPC")
        # print(f"{self.alignment}, {self.skills}, {self.senses}")

def enter_deets(name, combat_round, PC):
    while True:
        try:
            initiative = int(input(f"Enter initiative for {name}: "))
            ac = int(input(f"Enter AC for {name}: "))
            hp = int(input(f"Enter HP for {name}: "))
            while True:
                hpmaxcheck = input("Max HP if different from HP: ")
                if hpmaxcheck == "":
                    hpmax = hp
                    break
                else: 
                    hpmax = int(hpmaxcheck)
                    if hp > hpmax:
                        print(f"HP ({hp}) is greater than max HP ({hpmax})")
                        yes = input("Continue? y/any: ").lower()
                        if yes == "y":
                            break
                        else:
                            continue
                    else: break

            character = Character(name, ac)
            character.initiative = initiative
            character.hp = hp
            character.hpmax = hpmax
            if PC:
                character.is_player = True
            else: character.is_player = False
            index = 0
            while index < len(combat_round) and combat_round[index].initiative >= initiative:
                index += 1
            combat_round.insert(index, character)
            return combat_round
        except ValueError:
            print("Integer values only.")

def select_players(combat_round):
    action = input("Add players from party? y/n: ").lower()

    if action == "y" or action == "":
        with open("player_characters.txt", "r") as file:
            player_characters = [line.strip() for line in file]
        for name in player_characters:
            while True:
                choose = input(f"Add {name}? y/n: ").lower()
                if choose in ("", "y"):
                    combat_round=enter_deets(name, combat_round, PC = True)
                    break
                elif choose == "n":
                    break
                else:
                    print("Invalid choice.")
    while True:
        add_player = input("Add another player? y/n: ")
        if add_player == "y":
            while True:
                name = input("Player Character name: ").title()
                if any(character.name == name for character in combat_round):
                    print("Choose a unique name.")
                    continue
                else: break
            combat_round=enter_deets(name, combat_round, PC = True)
            continue
        else: break
    return combat_round

def select_encounter(combat_round):
    add_encounter = input("Add a saved encounter? y/n: ").lower()
    if add_encounter =="y" or add_encounter == "":
        with open("saved_encounters.txt", "r") as file:
            encounters = json.load(file)
        print("\nAvailable Encounters:")
        for i, encounter in enumerate(encounters, 1):
            print(f"{i}. {encounter['name']}")
        print(f"{i+1}. Exit")
        while True:
            try:
                selected_encounter_index = int(input("Select an encounter: ")) - 1
                if selected_encounter_index == len(encounters):
                    selected_encounter = "Exit"
                    break
                elif selected_encounter_index < 0:
                    print("Selection cannot be zero or negative.")
                elif selected_encounter_index >= len(encounters):
                    print("Selection too high to be an encounter.")
                                 
                else:
                    selected_encounter = encounters[selected_encounter_index]
                    for character_data in selected_encounter["characters"]:
                        character = Character(character_data["name"],character_data["ac"])
                        character.init_dice = character_data["initiative"]
                        character.hp_dice = character_data["hp"]
                        character.is_player = False
                        character.resolve_character()
                        character.hpmax = character.hp
                        combat_round.append(character)
                    break 
                    
            except ValueError:
                print("Invalid input.")
            
    while True:
        add_NPC = input("\nAdd another NPC? y/n: ").lower()
        if add_NPC == "y":
            while True:
                name = input("NPC player name: ").title()
                if any(character.name == name for character in combat_round):
                    print("Choose a unique name.")
                    continue
                else: break
            combat_round = enter_deets(name, combat_round, PC = False)
            continue
        else: break

    combat_round.sort(key=lambda character: character.initiative, reverse=True)
    return combat_round

def print_order(combat_round):
    print("\nInitiative order:\n")
    for i, character in enumerate(combat_round, 1):
        print(f"{character.name}\nAC: {character.ac}, HP: {character.hp}")
        if character.conditions:
            conditions_str = ', '.join(character.conditions)
            print(f"Conditions: {conditions_str}")
        if character is combatant:
            print("^^^^^^^^^^^^^^")

def choose_char(combat_round):
    for i, character in enumerate(combat_round, 1):
        print(f"{i}: {character.name}")
    choose = int(input("choose a character: ")) -1
    chosen = combat_round[choose]
    return chosen

def win_state_check():
    combat_end = False
    if all("Unconscious" in character.conditions or ("Incapacitated" in character.conditions) for character in combat_round):
        print("\nAll combatants are incapacitated!")
        print("Remove status from a character?")
        chosen=choose_char(combat_round)
        chosen.remove_condition()
        combat_end = True
    if all(character.is_player for character in combat_round):
        print("\nCombat over! A winner is You!")
        combat_end = True
    if all(not character.is_player or ("Unconscious" in character.conditions and character.is_player) or ("Incapacitated" in character.conditions and character.is_player) for character in combat_round ):
        print("\nTotal Party Knockout!\nYou have met a terrible fate!")
        combat_end = True
    if len(combat_round)==1:
        print(f"\nA Winner is {combatant.name}!")
        combat_end = True
    return combat_end

while True:
    turn_number = 0
    round_number = 0
    combat_round=[]
    combat_round=select_players(combat_round)
    combat_round=select_encounter(combat_round)
    combat_round.sort(key=lambda character: character.initiative, reverse=True)
    combatant_index = 0
    while combat_round:
        turn_number += 1
        if combatant_index == 0:
            round_number += 1
            turn_number = 1
        combatant = combat_round[combatant_index]
        combat_end=win_state_check()
        if combat_end:
            break
        while True:
            if combatant not in combat_round:
                combatant_index = (combatant_index + 1) % len(combat_round)
                break
            print_order(combat_round)
            print(f"\nRound {round_number}, Turn {turn_number}\nIt's {combatant.name}'s turn!")
            if combatant.dying:
                print(f"Death saves\nSuccess: {combatant.death_save_success}\nFailure: {combatant.death_save_failure}")
                combatant.death_save()
                combatant_index = (combatant_index + 1) % len(combat_round)
                break
            if "Unconscious" in combatant.conditions or "Incapacitated" in combatant.conditions or combatant not in combat_round:
                input(f"{combatant.name} is unable to act!")
                combatant_index = (combatant_index + 1) % len(combat_round)
                break
            
            action = input("(C)onditions, (h)p, (p)layers, (i)nspect, (e)nd turn: ").lower()
            print("")
            if action == "e":
                combatant_index = (combatant_index + 1) % len(combat_round)
                break

            elif action == "p":
                action = input(f"(A)dd new player or (r)emove a player?: ").lower()
                if action == "a":
                    while True:
                        name = input("New player name: ").title()
                        if any(character.name == name for character in combat_round):
                            print("Choose a unique name.")
                            continue
                        else: break
                    action = input("(P)C or (N)PC?: ").lower()
                    if action == "p":
                        combat_round = enter_deets(name, combat_round, PC=True)
                        combatant_index = combat_round.index(combatant)
                        continue
                    elif action == "n":
                        combat_round = enter_deets(name, combat_round, PC=False)
                        combatant_index = combat_round.index(combatant)
                        continue
                    else: continue
                elif action == "r":
                    print("Combatants to remove:")
                    chosen=choose_char(combat_round)
                    combat_round.remove(chosen)
                    continue
                else: continue
            elif action == "c" or action == "h" or action == "i":
                chosen=choose_char(combat_round)
                if action == "c":
                    if chosen.conditions:
                        action = input("(A)dd or (R)emove a condition?: ").lower()
                        if action == "a":
                            chosen.add_condition()
                        elif action =="r":
                            chosen.remove_condition()
                        else: continue
                    else: chosen.add_condition()

                if action == "h":
                    action = input("(H)eal or (D)amage HP?: ").lower()
                    if action == "h":
                        heal = int(input(f"\nHeal {chosen.name} by how much: "))
                        chosen.heal_damage(heal)
                    elif action =="d":
                        damage = int(input(f"\nDamage {chosen.name} by how much: "))
                        chosen.take_damage(damage, combat_round)
                    else: continue

                if action == "i":
                    chosen.display_info()
                    if chosen.conditions:
                        action = input("See descriptions for conditions? y/n: ").lower()
                        if action == "y":
                            print("")
                            chosen.describe_conditions()
                    input("\nPress any key to continue\n")
            else: continue