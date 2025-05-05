import random

def generate_goose_fact():
    facts = ["Male geese are called 'Ganders'.", 
             "Geese eat seeds, nuts, grass, plants and berries", 
             "When flying in groups, geese trade off the leader position to avoid tiring out.", 
             "Geese are loyal, they mate for life!", 
             "Geese can be social with other species if they are raised together.", 
             "Geese enjoy doing home improvements with sticks and leaves.", 
             "Geese are some of the best navigators due to their amazing vision!",
             "Airports use loud sounds like propane cannons to scare away geese.",
             "A mother goose may travel more than 20 miles from their nest in search of food.",
             "Geese can live for anywhere between 10 and 25 years!",
             "Geese are very territorial... But you already knew that.",
             "Geese can fly while sleeping, a process called 'unihemispheric slow wave sleep'!",
             "Despite not being nocturnal, Geese can see fine in the dark.",
             "During winter, geese may stand on one leg to preserve body heat.",
             "Geese may be able to see a wider range of colors than humans!",
             "It is legal to own waterfowl, like geese, in most states.",
             "Geese can fly at speeds of up to 70 mph!",
             "Foxes, coyotes and raccoons are some of many the predators to geese.",
             "Canadian geese are protected by law, the Migratory Bird Treaty Act.",
             "Predator decoys such as alligators are an effective method of keeping geese away.",
             "Geese find the smell of artificial grape flavor, such as kool-aid, repulsive.",
             "Geese are said to be very loyal pets, if domesticated.",
             "Geese kept as pets have been known to nibble their owners, affectionately."
             ]
    
    num = random.randint(0,len(facts))
    return (facts[num-1], num)