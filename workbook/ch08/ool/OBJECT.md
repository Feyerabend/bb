
## Object structures

This chapter describes basic (but not all) object structures found in Java. These are the linguistic starting points for designing object-oriented programs in Java. The object structures also show those_possibility_ available to write programs in Java.

### Imperative programming

Java is what is called an object-oriented language. This means that the structure of programs can be built with tools from theories about what constitutes object orientation. The theories are based on concepts about objects, classes, methods, inheritance, instances, message handling, etc. But the language also allows within itself an older type of programming that will be called hereafter_imperative programming_. The imperative programming is still an essential part of how the programs are finally run (executed). It is within the object-oriented shell that the imperative programming in Java resides.

Imperative programming is based on building blocks that are close to how algorithms are usually described. A recipe for baking e.g. can constitute an algorithm for how to go about baking buns. Heat the oven to 200 degrees, take a certain amount of flour and milk and yeast, stir these together, etc. hopefully resulting in baked buns. Algorithms are thus descriptions of approaches (procedures). (The closest you get to pure procedures are static methods in Java. These can be used in imperative programming, without object orientation ever being needed.)

In order to e.g. convert degrees of heat specified in Fahrenheit to Celsius there is a simpler formula: the number of degrees in Fahrenheit minus 32, times 5/9. In Java, e.g. the imperative part of the program is written:

```java
    int lower, upper, step;
    float fahr, celsius;

    lower = 0;
    upper = 300;
    step = 20;

    drive = lower;

    while (fahr <= upper) {
        celsius = (5.0f / 9.0f) \* (fahr - 32.0f);
        System.out.println("Fahrenheit = " + fahr
            + " equals Celsius = " + celsius);
        fahr += step;
    }
```

The basic structure here is first declarations of which variables are used, initialization of the variables, and finally an iteration (loop) that prints a smaller list. The printed list itself will consist of values ​​in Fahrenheit from 0 to 300 at 20 degree intervals, and its equivalent in Celsius.

### Object orientation

Object-orientation faces a completely different approach to programming. Although in practice imperative programming is most often used within the object-oriented shell of Java, it is not essential to the object structure itself.

Objects can be thought of as having some kind of state (data) and certain behaviors. Classes are then a kind of abstractions of these objects. If algorithms are usually compared to recipes, the object-oriented ideas are usually compared to concrete objects that we have around us, e.g. bicycles.

Assuming that bicycles exist in some bicycle models and the bicycle models are instantiated in some concrete bicycles sold by bicycle sellers, the bicycle models can be likened to classes and the concrete instances themselves to objects. A bicycle model has conditions such as the number of gears, how many wheels there are, what size of wheels and tires there are, but also methods such as how to shift the model of bicycle, how to brake the model of bicycle. A children's bike model has completely different conditions and methods than an adult bike model. The very concept of bicycle can also be said to be a certain kind of class, an abstract class that can only be concretized in real bicycle models. Java's class concept in general seems to allow what in theories of programming are called abstract data types, data types that can be based on already defined types (API).

If, on the other hand, we start from the ideas of object-orientation, the abstractions become more freed from the analogy of objects to concrete bicycles. Here we are talking about agents that in the mind correspond to objects, but also messages that are sent to the agents. An activation occurs when an agent receives a message, and it accepts and thus takes responsibility for a certain intended action, and performs a certain method that fulfills the request or task that has been given to the agent. The agent does not itself have to perform exactly the tasks it has accepted to perform (but not imposed), but can pass the message on (delegate) to others (objects).

Messages are thus more abstracted than the mere invocation of methods. It is not until the agent has accepted the message that it also takes responsibility for executing (calling) certain method. During the execution of the program, other agents may come into question and are not determined beforehand. In fact, many variations on methods can be applied before the program is run, when they are finally decided. By the agent taking responsibility for the execution of a request or task, his interpretation of it can also independently determine how he should proceed to solve the task. This important property results in an interface between the tasks to the agent and the execution itself, between the protocol (all the object's responsibilities) and the implementation. In this way, data can also be protected and executions can be encapsulated from influence or insight from the outside. (It is also in the corresponding way that the type of the object can be distinguished from its implementation.)

Java has a simple class hierarchy, meaning that classes branch where all branches grow apart and never together. New branches grow from the old ones. One sometimes speaks of classes with parental characteristics (parent, ancestral) higher up in the hierarchy. Given a certain class, the parent is superclass. This is the parent of the subclass that inherits behaviors (methods) and states (data) from the superclass. All classes inherit a parent class: the Object class. There is also a separate subtype hierarchy by so-called interfaces can inherit from each other.

A very useful feature of object-oriented languages ​​is polymorphism. The polymorphism means that e.g. methods can be varied so that similar conceptual names can be used for similar purposes. Comparing green, red or yellow apples to each other is in a sense similar to comparing brown and green pears. The comparisons have a certain similarity to each other even though they are about different types of objects: apples and pears with the common element being that they are of the same type; they are fruits. In an analogous way, Java has the opportunity to use methods in a number of different ways through e.g. method overriding and method overlay.

Some object-oriented concepts related to Java

*   _Class_, Data structures (variables) with associated methods.
*   _Object_, instance of class. There can be multiple instances of the same class.    
*   _Hierarchy_, Structure of classes that inherit each other in a certain order.
*   _Number_, Subclasses can inherit methods and variables from a superclass.    
*   _Super class_, Class higher up in the hierarchy than its offspring subclasses.
*   _Subclass_, Class below parent class.    
*   _of the subclass_, The formation of a new class inheriting from some superclass.
*   _Polymorphism_, Ability to substitute objects for other objects with matching interfaces at runtime.
    

## Classes and methods

The object-orientation in Java negates the need for imperative order for its own structure. A class is shown in Listing 2.1.

**List 2.1**

```java
class StoreClass {
    int x = 0;

    void setValue(int value) {
        x = value;
    }
    int getValue() {
        return x;
    }
}
```

The relative order of the elements does not matter. However, the order of the code within setValue() and getValue() is important. The class could also be written:

```java
class StoreClass {
    int getValue() {
        return x;
    }

    int x = 0;

    void setValue(int value) {
        x = value;
    }
}
```

The class has two methods.

```java
    ...
    int getValue() { ... }
    void setValue(int value) { ... }
    ...
```

The methods in Java consist of a signature and a body. The body is what is put in brackets. One_signature_ in turn consists of the return value type, the name of the method and a list of parameters with their respective types. The return value obtained from the method when it is called can be e.g. a primitive integer type int. But the method may not return any value. The return value will be empty: void. Also class names can be return value types like Integer (data type class for int).

A parameter consists of type and parameter variable. Multiple parameters are separated by commas. Sometimes methods can have no parameters and then consist of empty parentheses.

In the class there is a clause that declares the value. The variable is similar to local variables.

```java
int x = 0;
```

But this is not a local variable, but one_instance variable_. The variable x is created when the object is created, i.e. an instance of StoreClass. A local variable, on the other hand, only exists within blocks or methods.

One of the methods explicitly returns a value while the other only sets a value. When the declaration of the method ends, the call to the method also ends and therefore no explicit termination is needed. The getValue() method explicitly returns the value the instance variable has through return. The control return is of the imperative kind rather than object oriented. The method getValue() could contain several different kinds of possible values ​​and a precise indication of which value is to be returned must be included. When an instance is created, the instance variable will be set to 0 by the statement that declares x as an integer and sets x to zero. This statement is declared in a field outside the methods.

Listing 2.2 shows examples of simulating how the memory button works on a simple calculator.

**List 2.2**

```java
class MemoryClass {
    int memory = 0;
    void memoryPlus(int value) {
        memory += value;
    }

    int remindMemory() {
        return memory;
    }

    void clearMemory() {
        memory = 0;
    }
}
```

Both the class in Listing 2.1 and the class in Listing 2.2 show encapsulation examples. The classes protect some data within them, which is accessed via methods. The methods are: getValue(), setValue() and respectively memoryPlus(), remindMemory() and clearMemory(). In each class there is also a container for data: value and memory respectively. This type of classes are called_data manager_ (data managers, data, state).

Other types of classes are e.g. data producers (data sources), data consumers (data sinks), observers (observer) or display classes (view). A consumer class can e.g. receive data from a text and look up certain matching words. A producer class can generate numbers that represent pixels for an image. Classes that handle drawing things on a screen can often be separated from the model that represents the things. A display class can handle drawing and updating perspective houses to a screen, allowing walkthroughs of the virtual building. While the model of the houses does not contain drawing data, the model may contain dimensions or connections between different objects such as walls and roofs. The model can be refined and standardize architectural drawings. This allows other display classes to reuse the model of buildings for other purposes.

## Object instances and method calls

Once the class is defined with methods and fields (above instance variables), it can be instantiated. During instantiation, objects are created. The objects are created using the new operator:

```java
    new StoreClass()
```

A variable of the same type is declared:

```java
    StoreClass mem
```

then everything can be put together into a statement where the variable is assigned to the object:

```java
    StoreClass mem = new StoreClass();
```

All Java reference types (classes, indexes, or interfaces) form types. When the new operator operates, it creates space for an object and instantiates the instance variables. The idea of ​​objects is also that they are multiplied from the same class:

```java
    StoreClass firstmem = new StoreClass();
    StoreClass secondmem = new StoreClass();
    StoreClass thirdmem = new StoreClass();
```

Now the methods can be invoked (be invoked) from Listing 2.2:

```java
    MemoryClass calc = new MemoryClass();
    calc.memoryPlus(67);
    calc.memoryPlus(23);
    calc.memoryPlus(98);

    System.out.println(calc.remindMemory());
    calc.clearMemory();

    System.out.println(calc.remindMemory());
```

The statements that follow each other calculate the sum of 67 + 23 + 98, print the sum 188, and then clear the memory and print 0. From the beginning at instantiation, the initial value is 0 in the memory held by the counter MemoryClass by declaring and initializing the instance variable at the same time.

Objects can of course be used when other classes and methods are called, as shown in Listing 2.3.

**List 2.3**

```java
class PrintEnclosedString {
    Printer output = new Printer();

    void enclosedPrint(String s) {
        output.print("{" + s + "}");
    }

    void enclosedPrintln(String s) {
        enclosedPrint(s);
        output.print("\\n");
    }
}

class Printer {
    void print(String s) {
        System.out.print(s);
    }
}
```

_The null term, garbage collection, and the finalize method_

The root term null (the special value or keyword) is useful to mark that_not_ exists instance of any object. When defining reference type variables, Java automatically sets its value to null. By using null as a reference that there is no object, you can easily test variables, return values ​​or parameters to see if a referenced object exists or not.

The other thing that is useful with null is when e.g. variables cease to refer to objects that the objects thus stand for_garbage collection_ (garbage collection). If e.g. a local variable is used for the reference to an object:

```java
    StoreClass x = new StoreClass();
    x.setValue(64);
```

it can be reused to refer to another object:

```java
    x = new StoreClass(1024);
```

If the variable is explicitly set to null within the block in which the local variable is located, the objects are candidates for garbage collection, as the scope only covers the block's start and end point:

```java
    x = null;
```

But this is strictly speaking not necessary. Since Java has automatic garbage collection, it means that the programmer does not need to keep track of when an object has been used completely and the collection is done implicitly instead.

When garbage collection starts, the conventionally defined method finalize() is called with the return type void. Common times when finalize() is overridden are when system resources have been used such as graphics contexts, the closing of network connections, or the removal of file descriptors (except for automatic memory management which is handled implicitly). In this special method that can be used in all classes, there should be a super.finalize() at the end to allow the superclasses to clean up after themselves, as their methods are otherwise blocked (overridden):

```java
void finalize() {
    ...
    super.finalize();
}
```

The actual ship collection is in what is called a low-priority thread and only happens when Java gets time, but can also be called explicitly to a class method:

```java
System.gc();
```

## Constructors and Overrides

Constructors can be seen as a variant of methods that are called when objects are created. Methods are called after the objects are constructed. In the constructor, you usually put in what the objects are to be initialized with. Constructor calls occur automatically when an object is created.

The constructors have the same name as the class but have no return values. A default constructor instantiates the class when its object instance is created. Suppose an instance of a class is instantiated within another class:

```java
class TestANewMemory {
    ...
    ANewMemory test = new ANewMemory();
    ...
}
```

Here, the default constructor will be called in the class ANewMemoryClass, where the instance variable is initialized at the constructor call instead of at the declaration within the class:

```java
class ANewMemory {
    int x, y;

    ANewMemory() {
        x = 0;
        y = 0;
    }
}
```

After this, another constructor can be added to the same class, which initializes the variable with a value that is given only when the object (construction) is created:

```java
class AnotherNewMemory {
    int x, y;

    AnotherNewMemory() {
        x = 0;
        y = 0;
    }

    AnotherNewMemory(int \_x, int \_y) {
        x = \_x;
        y = \_y;
    }
}
```

To initialize this variant of class to new objects, write:

```java
class TestAnotherNewMemory {
    ...
    AnotherNewMemory test = new AnotherNewMemory(34, 56);
    ...
}
```

There are in AnotherNewMemory two constructors which_overlays_ each other. They are both part of the same class, have the same name but different number of parameters. (In general, they can also have different types of parameters even if the number is the same),

Since the constructor can be considered to some extent as the initializing method, the method override works like the constructor override for methods. An example where both types exist, where equals() uses the java.lang.String package where the method equalsIgnoreCase() delivers a comparison between strings regardless of whether they have lowercase or uppercase in them:

```java
class Name {
    String v;

    Name() { }

    Name(String _v) {
        v = _v;
    }

    boolean equals(String s) {
        return v.equalsIgnoreCase(s);
    }

    boolean equals(Name n) {
        return v.equalsIgnoreCase(n.getName());
    }
}
```

The reference "this" and "super"

A common convention used when initializing via constructor is that the same name of instance variables and parameters can be used. To distinguish them, the instance variables are referenced to it_the current object_with this. However, the parameters act within the constructor block as readable local variables. If some components in the above class are changed, we get:

```java
class AThirdNewMemory {
    int x, y;
    ...
    AThirdNewMemory(int x, int y) {
        this.x = x;
        this.y = y;
    }
}
```

A variant of class that accepts three arguments (parameters) to the constructor:

```java
class ADifferentNewMemory {
    int x, y;
    ...

    ADifferentNewMemory(int x, int y) {
        this.x = x;
        this.y = y;
    }

    ADifferentNewMemory(int x, int y, boolean a) {
        this(x, y);
        if (a) {
            this.x = x + y;
        } else {
            this.x = x - y;
        }
    }
}
```

The statement with this(x, y) refers to and matches the two-digit constructor immediately above, and executes the instructions in it before it executes the instructions in the constructor it is inside. The variables x and y have thus already been given values ​​before they are manipulated with addition or subtraction in the rest of the constructor.

If no default constructor (constructor with no arguments) exists, Java will execute the program as if there were a default constructor. The assumed constructor calls the superclass's default constructor. This is effectively the same as if there had been a default constructor:

```java
class YetAMemory {
    ...
    YetAMemory() {
        super();
    }
}
```

## .. of the subclass

One of the most useful phenomena in object orientation is inheritance. Inheritance involves, among other things, subclassing and the ability to build hierarchies of classes. By taking a class and extending it to a new class, the properties from the old one can still be maintained. The new class is a subclass (hence subclassing) of the old, where the old is the superclass. Assume that a class Name is extended to ExtendedName, Listing 2.4.

**List 2.4**

```java
class Name {
    String v;

    Name() { }

    Name(String \_v) {
        v = \_v;
    }

    String getName() {
        return v;
    }

    boolean equals(String s) {
        return v.equalsIgnoreCase(s);
    }

    boolean equals(Name n) {
        return v.equalsIgnoreCase(n.getName());
    }

    void print() {
        System.out.print(v);
    }
}

class ExtendedName extends Name {
    String pr, po;

    ExtendedName(String _pr, String _v, String _po) {
        super(_v);
        pr = _pr;
        po = _po;
    }

    String getPre() {
        return pr;
    }

    String getPost() {
        return po;
    }

    String extendName() {
        return concat();
    }

    String extendValue() {
        return super.value = concat();
    }

    String concat() {
        return pr + super.value + po;
    }
}
```

In the Name class, there are constructors that are overridden, but also methods that are overridden and not overridden, and an instance variable.

A `print()` method is inherited:

```java
class Name {
    ...

    void print() {
        System.out.print(v);
    }
}

class ExtendedName {
    ...
}
```

When instantiating ExtendedName and calling print(), the inherited method will be called:

```java
    ExtendedName en = new ExtendedName(pre, middle, post);
    en.print();
```

### Super constructors and super variables

The constructor in `ExtendedName` takes advantage of being under (sub)class `Name`, by calling the constructor that receives a string in Name, `super(_v)`. The value of v is directly accessible from `ExtendedName`. The `super.v` in `extendValue()` in `ExtendedName` is therefore redundant here, since there is only one v in the context. But both super and this are sometimes used, for the sake of clarity, to explicitly mark which instances or superclasses are being referred to, except that they are sometimes necessary.

The `extendName()` and `extendValue()` methods illustrate different ways to return values. In the case of `extendName()` only the combination will be returned. In the case of `extendValue()`, the combination will not only be returned but also the value v will be set to this combination (concatenation, concatenation, juxtapose).

## Method Override

Methods not only need to be inherited, they can __be replaced__ of other methods with the same name. Then a method is written that overrides another method with the same name (strictly speaking the same signature) in the superclass. That is when a method in a derived class (subclass) has the same signature as a method in the parent class, the method is said to override the parent method. When a method traverses Java's tree structure of classes that extend each other, it searches up the hierarchy from subclasses to superclasses until it reaches the top class Object. If the search does not find a matching method, an error is returned.

The `Name` and `ExtendedName` classes can be supplemented with the `toString()` methods:

```java
class Name {
    ...
    String toString() {
        return "Value: \[" + v + "\]";
    }
}

class ExtendedName extends Name {
    ...
    String toString() {
        return "Pre: \[" + pr + "\]\\n"
            \+ "Post: \[" + po + "\]";
    }
}
```

### Super methods and scope

If the previous method toString() in ExtendedName rather for replacement method, a refinement is written:

```java
class ExtendedName extends Name {
    ...
    String toString() {
        return "Pre: \[" + pr + "\]\\n"
            \+ super.toString()
            \+ "Post: \[" + po + "\]";
    }
}
```

so the overriding method uses the overridden method. It calls the toString() method of Name via super.toString(). There is some symmetry between methods, variables and constructors when it comes to this and super. In both cases only when there is doubt about what is meant do these markers need to be used explicitly and not otherwise. To distinguish local variables from instance variables, this was previously inserted. The range for Java will be the first to search for e.g. a variable's declaration within the method's braces, then within the class, and later up through the hierarchy of extended classes towards Object.

Some concepts related to calls and references

*   this, this object    
*   super, super classes
*   super._method name_(), calls the super class's method    
*   this(), matching constructor in the class
*   super(), matching constructor in the superclass    
*   return _value_, return the following value
    

## Abstract classes and methods

Java includes the abstract modifier to declare methods or classes as abstract. That a class is abstract means that_smallest_ one method is abstract, while the others may be non-abstract. Abstract methods are used e.g. as behavior is not implemented within the class, but within the class's extension. Assuming there is a class with some methods and variables, as well as a declared abstract method last:

```java
abstract class Pen {
    int x, y;

    int getX() {
        return x;
    }

    int getY() {
        return y;
    }

    void setX(int a) {
        x = a;
    }

    void setY(int b) {
        y = b;
    }

    void drawTo(int a, int b) {
        drawFromTo(getX(), getY(), a, b);
        moveTo(a, b);
    }

    abstract void drawFromTo(int x, int y, int a, int b);
}
```

The Pen class defines a kind of abstract pen for a two-dimensional plane. It can keep track of the x and y coordinates, move the pen to new coordinates, and draw lines between already stored starting points and new specified coordinates. Still it doesn't draw anything on screen or plotter (printer). The abstract method drawFromTo() is defined but not implemented. Nor can objects be formed from this class; the class cannot be instantiated.

In order for Java to be able to use the class, Pen can be extended to DrawablePen. The drawFormTo() method is overridden where the drawLine() method is in the default Graphics class:

```java
class DrawablePen extends Pen {
    java.awt.Graphics g;

    DrawablePen(java.awt.Graphics _g) {
        g = _g;
    }

    void drawFromTo(int x, int y, int a, int b) {
        g.java.awt.Graphics.drawLine(x, y, a, b);
    }

    void disposeGraphics() {
        g.java.awt.Graphics.dispose();
        System.gc();
    }

    void finalize() {
        disposeGraphics();
        super.finalize();
    }
}
```

Methods with the modifier or the access (access) static or private cannot be declared abstract. Neither can constructors be declared abstract. Commonly, a conventional method called init() replaces the constructor in an abstract class.

## Interface

A language part in Java that is close to abstract classes and methods is interface. An interface is much like a collection of abstract methods. Interfaces can be declared abstract despite being redundant:

```java
abstract interface Transferable {
    ...
}
```

The interfaces can contain declarations of methods and class constants:

```java
interface Transferable {
    void subject(String subject);
    void letter(String letter) throws TransferException;
    ...
}
```

Interfaces (like abstract classes) cannot be instantiated, because there is nothing to instantiate. But they can replace so-called multiple inheritance. By being able to implement several interfaces but only inherit (extend) a tree, multiple inheritance can be simulated.

The interface Transferable is implemented in two classes, firstly Printer:

```java
class Printer
    implements Transferable {
    public void subject(String subject) {
        ...
    }

    public void letter(String letter)
    throws TranferException {
        ...
    }
}
```

and partly Mailer:

```java
class Mailer
    implements Transferable {
        public void subject(String subject) {
        ...
    }

    public void letter(String letter)
    throws TranferException {
        ...
    }
}
```

The classes Printer and Mailer must contain declarations of the methods that the interface promises (however, of course, the implementations can be further delegated). The methods do not have to perform anything, but can of course be empty. The classes certainly do not extend other classes and could e.g. have extended an abstract Transferable instead. But Mailer could also extend a more general SMTP class or Printer a more general Printer class. This is why interfaces exist. Although the names (signatures) of the methods implemented are identical, similar behavior is expected. Nevertheless, completely different tasks will be performed by each class. The calling class therefore does not need to interfere with the particular implementation within the methods.


### Multiple interfaces

Interfaces can form their own subtype hierarchy where interfaces can extend other interfaces:

```java
interface SetAccess {
    void set(Object key, Object value);
}

interface GetAccess {
    Object get(Object key);

}

interface Access extends SetAccess, GetAccess {

}
```

Thus, a class can e.g. implement parts of a particular type and not the entire stipulated type. In this case, e.g. the access method set() is only implemented in a class without get() being needed or vice versa.

## Classes "Object"

At the top of the class hierarchy is the Object class. Only one parent (superclass) exists for each class except Object, but each class can have more descendants (subclasses). Therefore, Object is the ultimate superclass, or what is called the root class, from which all other classes inherit their properties. Most of the time, only some of the methods in Object are used, while others are overridden.

Previous definition of toString() is example of method being overridden. The purpose of this is to form a string representation of an object. For the most part, therefore, the toString() method is overridden in many of Java's standard classes. It is the one that will be called if any object's string representation is to be printed within e.g. System.out.println().

Other methods are equals() in Object which compares whether two objects contain the same values. If equals() is overridden, all the objects the class refers to should be (recursively) compared. (Another method is e.g. clone() which can be overridden if the class implements the Clonable interface, which copies the objects. Again, the class should recursively copy all the objects referenced in the class.)

SORRY, HERE IT ENDS

_**(Reflection & Class literals) -- not finished**_

_**Data type classes**_

finished but not entered episodes:

_**Typomvandling**_

_**Predikatet "instanceof"**_

_**Modifier**_

_**Class variables**_

_**Class methods**_

_**Instance initializer**_

_**Blank finals, final parameters, and final local variables**_

_**Inner classes**_

_**Anonymous classes**_

_**Local classes**_

(nested classes --> moved)

_**Parameterized types (item 1.2)**_

_**Packages & javadoc**_