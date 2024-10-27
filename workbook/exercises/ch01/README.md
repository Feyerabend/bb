## Exercises

### Simple data types

####  Integers

1. *What are the limitations of using an 8-bit binary system to represent integers?*
    - Examine the constraints this system imposes on the range of integers and discuss its effects on overflow errors in computations.

2. *Explain the difference between signed and unsigned integer representation.*
    - How does this difference impact the range of representable values, and why is it crucial in certain applications?

3.	*Describe the concept of 2’s complement representation in an 8-bit system.*
    - Investigate how this approach allows representation of negative integers, and explain how it differs from other binary representations.

4.	*In an 8-bit system, calculate the binary representation of -25 using 2’s complement.*
    - Show each step and discuss why each is necessary to properly encode the value.

5.	*What are the main challenges of converting a decimal integer, such as 123, into binary form?*
    - Analyze the process and potential sources of error, focusing on practical difficulties in manual and programmatic conversion.

6.	*How does sign extension work when converting an 8-bit signed integer to a larger bit size (e.g., 16 bits)?*
    - Explain why this method preserves the integer’s value and how it differs for positive and negative numbers.

7.	*Discuss the implications of overflow in an 8-bit integer system.*
    - When does overflow occur, and how might it impact real-world applications that rely on integer computations?

8.	*Convert the integer 200 to binary in an 8-bit system and interpret its result in both signed and unsigned formats.*
    - Compare the meaning of this binary sequence under each interpretation and explain the discrepancy.

9.	*How does using 16-bit or 32-bit systems address some limitations seen in 8-bit integer representation?*
    - Describe the increased range and precision available and the trade-offs, such as memory usage.

10.	*Investigate the binary representations of 127 and -128 in an 8-bit signed integer system.*
    - Explain how these values are encoded and why they represent the maximum and minimum values, respectively.

11.	*Explain how integer rounding differs from rounding with floating-point numbers in a computer system.*
    - Explore the precision limitations and how each system approaches rounding during computations.

12.	*Explore the concept of arithmetic overflow with a signed 8-bit integer during addition.*
    - Provide examples to illustrate how overflow might occur when adding numbers near the upper or lower bounds of the integer range.


#### Floating-point numbers

1. *What difficulties are there with representing rational numbers in floating point on computers? Limitations?*
    - Investigate the inherent challenges and limitations of using floating-point representation for rational numbers.

2. *Are there other ways to represent fractions in computers?*
    - Explore different ways to represent fractional numbers, such as fixed-point representation or rational number representations.

3. *What is fixed point representation, and how would an implementation look like in Python? In C?*
    - Compare fixed-point representation with floating-point representation, and examine practical implementations in multiple programming languages.

4. *What are the pros and cons of using floating point versus fixed point representations?*
    - Analyze the advantages and disadvantages of each representation method to determine their suitability for various applications.

5. *How do rounding modes in floating-point arithmetic affect results?*
    - Examine the different rounding modes defined by the IEEE 754 standard and their implications for numerical accuracy.

6. *What are the common pitfalls when using floating-point numbers in algorithms?*
    - Identify typical mistakes or misunderstandings that can lead to inaccurate results or unexpected behaviors.

7. *How does the choice of data type (float vs. double) influence precision and memory usage?*
    - Discuss the trade-offs between using single-precision (float) and double-precision (double) floating-point representations.

8. *Can you explain the concept of `denormalized numbers' in floating-point representation?*
    - Delve into how denormalized numbers work and their significance in representing very small values.

9. *What role does floating-point arithmetic play in graphics programming?*
    - Explore how floating-point numbers are utilized in rendering, transformations, and other aspects of computer graphics.

10. *How can understanding floating-point representation improve debugging and error analysis in programs?*
    - Discuss how knowledge of floating-point arithmetic can aid in diagnosing numerical issues in code.

11. *What are some real-world applications that heavily rely on floating-point computations?*
    - Identify fields such as scientific computing, machine learning, and finance where floating-point arithmetic is crucial.

12. *Could you provide me with references for further reading on floating-point numbers?*
    - Seek additional resources to deepen your understanding and broaden your knowledge of floating-point arithmetic.


#### Characters and ASCII

1. *Describe the ASCII encoding system.*
    - Explain how ASCII represents characters as binary numbers and the limitations this encoding imposes on representing non-Latin characters.

2. *Explain how the character ‘A’ is represented in ASCII.*
    - Discuss the binary encoding and what each bit represents. Extend this explanation to lowercase letters and punctuation marks, noting the significance of the uppercase/lowercase distinction.

3. *Trace the development of character encoding systems before ASCII.*
    - Investigate earlier encoding systems, such as Morse code or telegraphy codes, and discuss how these influenced ASCII’s design.

4. *Why was the development of Unicode necessary despite the success of ASCII?*
    - Examine the limitations of ASCII in representing diverse characters and languages and how these limitations affected global computing.

5. *Explain the concept of character encoding in ASCII compared to UTF-8.*
    - Analyze the differences in bit usage between ASCII’s 7-bit encoding and UTF-8’s variable-length encoding, and discuss how UTF-8 supports a much wider range of characters.

6. *Provide the binary encoding of the ASCII characters for ‘Hello’.*
    - Show each letter’s binary representation, and explain the pattern you observe in encoding uppercase vs. lowercase letters.

7. *Discuss how ASCII’s 7-bit design influenced early computing hardware.*
    - Research why ASCII was initially designed as a 7-bit code and how this choice affected memory and data transmission in early computer systems.

8. *What role did ASCII play in early internet communication?*
    - Investigate ASCII’s use in early internet protocols (such as email and HTTP) and explain why its simplicity was advantageous for these applications.

9. *Describe how UTF-8 encodes characters that are not part of ASCII.*
    - Give examples of how UTF-8 uses more than one byte to represent non-Latin characters and discuss the benefits and potential challenges of variable-length encoding.

10. *Convert the decimal ASCII values of the characters in “Data” to binary.*
    - Explain each step and analyze the differences in encoding uppercase and lowercase letters.

11. *Explore the historical evolution from ASCII to Extended ASCII.*
    - Describe the differences and explain how Extended ASCII attempted to represent additional characters. Consider why this solution was still insufficient for global use.

12. *Why does UTF-8 remain the dominant encoding standard on the web today?*
    - Discuss UTF-8’s advantages over other encoding standards, such as UTF-16 or ISO-8859, particularly for web applications and multilingual content.

13. *Research the historical challenges in creating a unified encoding standard like Unicode.*
    - Investigate early challenges faced by the Unicode Consortium in standardizing characters for global use and how cultural and linguistic diversity influenced these decisions.

14. *What was the significance of the space character’s encoding in ASCII?*
    - Explain why the space character (00100000 in ASCII) has its particular encoding and its importance in text processing and data storage.

15. *Discuss the use of control characters in ASCII.*
    - Examine ASCII’s control characters (such as newline and carriage return) and their impact on early text processing and communication protocols.



#### Strings


1. *Explain how a string such as “Data” is stored in memory.*
    - Break down each character’s ASCII binary representation and explain how these are stored consecutively, including the role of the null character at the end.

2. *What challenges arise when using the null character to indicate the end of a string?*
    - Discuss how this choice impacts memory usage and handling in programming languages, particularly in cases where binary data may include null values.

3. *Convert the string “Binary” into its ASCII binary representation.*
    - Show each character’s 8-bit encoding and analyze any patterns in the binary sequence based on uppercase vs. lowercase letters.

4. *Investigate the historical evolution of string handling in early programming languages.*
    - Explore how languages like C represented strings, the reliance on null-terminated strings, and the advantages and limitations of this approach.

5. *What is typecasting, and why is it important in programming?*
    - Explain how typecasting allows data to be converted from one type to another and give examples of cases where typecasting is essential (e.g., converting integers to floating-point numbers for division).

6. *In what ways does understanding binary representation aid in efficient data storage and manipulation?*
    - Discuss how knowing the binary layout of data types helps developers optimize storage and processing in applications that handle large volumes of data.

7. *How did early computer systems handle type distinctions, particularly for strings?*
    - Explore how early computing systems and languages distinguished types and the impact on memory usage and program efficiency.

8. *Describe the process of concatenating two strings in memory.*
    - Explain how binary sequences are combined when two strings are concatenated and any implications this has for memory allocation and management.

9. *Explain the significance of type systems in programming languages.*
    - Compare weakly and strongly typed languages, and discuss how type systems prevent errors and allow more robust code, especially in large-scale applications.

10. *Investigate how types represent more than just binary data in object-oriented programming.*
    - Explain how types, or classes, in languages like Python or Java define both data and the methods associated with that data, giving an example of how a “Person” class might combine attributes and methods.

11. *Research how string encoding has evolved from ASCII to Unicode in programming.*
    - Explain the limitations of ASCII in representing global characters and how Unicode’s broader encoding scheme has enabled support for a wider array of languages and symbols.

12. *Convert the string “Hello World!” into its binary ASCII representation.*
    - Display each character’s binary encoding and describe how punctuation and spaces are represented in the ASCII system.

13. *What are the advantages of null-terminated strings versus length-prefixed strings?*
    - Explore both methods for indicating the end of a string in memory, including any historical reasons for the adoption of null-terminated strings in languages like C.

14. *Discuss the importance of type safety in modern programming languages.*
    - Explain how type safety reduces errors and enhances code stability, giving examples of type-safe languages (e.g., Java) and those that are more permissive (e.g. JavaScript).

15. *Describe how strings can be manipulated at the binary level, such as reversing or encoding.*
    - Investigate common string operations, such as reversing or encrypting, and explain how these processes affect the underlying binary data.



### Variables

#### Assignment

#### Mutable and immutable

### Control structures

### Functions
#### Calling functions

