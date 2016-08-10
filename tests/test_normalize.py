from dockerrotate.images import normalize_tag_name

def test_normalize_tag_name():

    assert normalize_tag_name('some.domain.com/organization/image:tag') == 'organization/image'
    assert normalize_tag_name('organization/image:tag') == 'organization/image'
    assert normalize_tag_name('image:tag') == 'image'
