# Performance test linkscraper
## Case 1
### Specifications:
CPU: Intel 11th Gen Intel(R) Core(TM) i7-11370H @ 3.30GHz  
RAM: 16GB SODIMM DDR4 3200 MHz  

#### TEST 1:
Websites:  
ah.nl  
Started running on 9:15  
finished 14:35. runtime 5h and 20 minutes  


	RAM:
	2x terminal:		    gem 30MB
	2x python 3.10 runtime:	    gem 68MB
	
	CPU:
	2x terminal:		    gem 0.7%
	2x python 3.10 runtime:	    gem 2.1%
	
#### TEST 2:
Websites:  
dirk.nl & jumbo.com  
Started running 16:10  
jumbo finished 22:40 (5h and 30 minutes)  
dirk crashed

	RAM:
	3x terminal:		    gem 82MB
	3x python 3.10 runtime:	    gem 110MB
	
	CPU:
	3x terminal:		    gem 0.9%
	3x python 3.10 runtime:	    gem 5.3%

## Case 2
### Specifications:
CPU: Intel 8th Gen Intel(R) Core(TM) i7-8750H @ 2.2GHz  
RAM: 16GB SODIMM DDR4 2667 MHz  

#### TEST 3:
Websites:  
dirk.nl  
Started running 09:27  
Finished after 1h and 25 minutes

	RAM:
	1x terminal:		    gem 75MB
	1x python 3.10 runtime:	    gem 34MB
	
	CPU:
	1x terminal:		    gem 0.5%
	1x python 3.10 runtime:	    gem 0.6%
	
#### TEST 4:
Websites:  
ah.nl & jumbo.com  
Started running 11:07  
ah.nl finished after 5 minutes and 45 seconds  
jumbo.com finished after 1h 55 minutes and 54 seconds  
  
Note: this test has new and faster code that only scrapes the product category  

	RAM:
	2x terminal:		    gem 86MB
	2x python 3.10 runtime:	    gem 90MB
	
	CPU:
	2x terminal:		    gem 0.6%
	2x python 3.10 runtime:	    gem 9.5%

## Case 3
### Specifications:
CPU: Intel 11th Gen Intel(R) Core(TM) i7-11370H @ 3.30GHz  
RAM: 16GB SODIMM DDR4 3200 MHz  

#### TEST 5:
Websites:  
dirk.nl  
Started running 11:08  
TEST FAILED
  
Note: this test has new and faster code that only scrapes the product category  

	RAM:
	1x terminal:		    gem 23MB
	1x python 3.10 runtime:	    gem 30MB
	
	CPU:
	1x terminal:		    gem 0.2%
	1x python 3.10 runtime:	    gem 0.8%

#### TEST 6:
Websites:  
dirk.nl  
Started running 09:38
Finished after 3h 3 minutes and 26 seconds

Note: this test has new and faster code that only scrapes the product category  

	RAM:
	1x terminal:		    gem 39MB
	1x python 3.10 runtime:	    gem 33MB
	
	CPU:
	1x terminal:		    gem 0.2%
	1x python 3.10 runtime:	    gem 0.9%