I am building a restaurant order management ai agent system using langgraph.

I will explain you very clearly what i want and what is the architecture. i will also explain the nodes the state and the edges.
In the end i will give you test cases to simulate and to tell me whether they pass or not.

The rough plan is:
There will be a user. when the code runs the user will give an order. this will be taken as an input which i will type
This order should go to the llm. The order as of now should contain dish and the required quantity.
for simplicity purpose for now we will limit the order to one particular dish and whatever quantity the user wants.
the llm will have to extract the order name and the quantity from the user input.
if the user input is unrelated to food ordering, the llm should not process that and tell the user the same thing that is an ai
of food ordering and not a general purpose llm.

Once the llm has order dish and quantity
it will send that to a node called order_confirm
The task of this order confirm is to look at the menu (i will tell you the menu later in this prompt).
Then this node will decide one of 3 cases
the order is available
the order is partially available means quantity is not sufficient
the order is not available at all (dish being not in the menu or 0 quantity available)
it will put this in the status of the state (I will tell u the exact content of the langraph state as well)

Once the llm received this
if the status is confirmed (Full available) it should call another node called cook.
if the status is partial or not available it should again prompt the user to decide
the user can either place a new order or can confirm if he wants to go ahead with the partial order

This order retries will be limited to 3 attempts meaning if after 3 attempt the user is not satisfied the system will come to the END node

Now when the cook node is called
there can be 2 cases
either the cook is done then the status will be READY
and if the cook fails (we can use a prob function). give 40% chances of fail and 60% chance of success

if the cook fails there should be 1 more attempt allowed for cook to succeed. if the cook fails even after these
then the llm should issue a apology to the user and come to END state

if the cook succeeds, the status will be READY
and the next node will be called which is serve
similar to cook this also has 2 cases
serve pass or serve fail
this also has 2 retry attempt
if the serve fails 2 times then the llm should issue a apology to the user and come to END state

if the serve succeeds the status should become complete the llm should issue a message to the user saying your order is complete
if serve fails then cook should be called one more time to retry.
Note that if cook has exhausted its retry attempts then it should not cook again and llm should issue an apology and come to end state

Now the state of langgraph

there should be a annotated message be llm and user

there should be order details
dish name as str
required quantity as int
available quantity as string
order_confirm will write the available quantity by reading the menu
the llm should get to know the order confirm status by reading the state
if a dish is not available in the menu then orderconform should write 0 as avail quantity

then there should be status
each node will update the status as specified in the above rules
then order retry attempts which are 3
cook retry attempts which are 2
serve retry attempts which are 2
each time a failure happens and a node is retrying it should decrement the counter
if any retry counter becomes 0 it means it is over. llm should understand whether it has to give a retry or issue apology by reading this counter
in the end there should be final result whether the order was completed or not.

Write the code and ask if there are any open questions from your side then ask
i will give you some test scenarios to test later on


here the menu and availability
burger 10 pizza 5
chowmin 4 
pasta 6
use gemini 2.5 flash


here is the 3 test cases 

1. user ask unrelated questions 2 times then ordered somthing that is partially success then ordered again the dish which is fully available but cooking is falied so cook retryed and again failed hen the serverfailed so llm issued an apology and came to END state
2. user  30 pizza. this order should fail as 
3. user ordered 10 pasta . the order should be confirmed (as the quantity available should be read from the menu)
the cooking should be successful
the serve should be successful
so the order should be completed
