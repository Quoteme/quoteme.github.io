// @AUTHOR      : Luca Leon Happel
// @DATE        : 2020-04-06
// @DESCRIPTION : get URL Variables, similar to PHP's $_GET
export const get = (url=location.href) => Object.fromEntries(
	location.href
		.concat('?')			// add extra '?' if URL has no URLvars
		.split('?')[1]			// everythin after first '?'
		.split('&')				// array of vars, seperated by '&'
		.map(e => e.split('=')) // create [key, value] pairs from vars
	)
