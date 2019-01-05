import objc
import AddressBook as ab

def pythonize(objc_obj):
    if isinstance(objc_obj, objc.pyobjc_unicode):
        return str(objc_obj)
    elif isinstance(objc_obj, ab.NSDate):
        return objc_obj.description()
    elif isinstance(objc_obj, ab.NSCFDictionary):
        # implicitly assuming keys are strings...
        return {k.lower(): pythonize(objc_obj[k])
                for k in objc_obj.keys()}
    elif isinstance(objc_obj, ab.ABMultiValueCoreDataWrapper):
        return [pythonize(objc_obj.valueAtIndex_(index))
                for index in range(0, objc_obj.count())]


_default_skip_properties = frozenset(("com.apple.ABPersonMeProperty",
                                      "com.apple.ABImageData"))
def ab_person_to_dict(person, skip=None):
    skip = _default_skip_properties if skip is None else frozenset(skip)
    props = person.allProperties()
    return {prop.lower(): pythonize(person.valueForProperty_(prop))
            for prop in props if prop not in skip}

def searchByPhone(phone):
    address_book = ab.ABAddressBook.sharedAddressBook()
    keys = [None, 
    ab.kABPhoneHomeLabel,
    ab.kABPhoneMainLabel, 
    ab.kABPhoneMobileLabel, 
    ab.kABPhoneWorkLabel,
    ab.kABPhoneiPhoneLabel, 
    ab.kABHomeLabel, 
    ab.kABWorkLabel, 
    ab.kABOtherLabel]
    criteria = []
    for label in keys:
        criteria.append(ab.ABPerson.searchElementForProperty_label_key_value_comparison_(
            ab.kABPhoneProperty,
            label, None,
            phone,
            ab.kABContainsSubStringCaseInsensitive
        ))
    search = ab.ABSearchElement.searchElementForConjunction_children_(ab.kABSearchOr, criteria)
    people = address_book.recordsMatchingSearchElement_(search)
    people = [ab_person_to_dict(person) for person in people]
    if len(people) > 0:
        match = people[0]
        if "middle" in match:
            key = '{} {} {}'.format(match.get('first', ''), match.get('middle', ''), match.get('last', '')).strip()
        else:
            key = '{} {}'.format(match.get('first', ''), match.get('last', '')).strip()
        return key
    return None