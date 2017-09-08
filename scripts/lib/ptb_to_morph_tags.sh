#!/usr/bin/bash
# converts PTB tags to the limited morpha tag set

perl -pe 's/_NNP.*$/_NP/' | perl -pe 's/_V.*$/_V/' | perl -pe 's/_MD/_V/' | perl -pe 's/_POS/_\$/'
