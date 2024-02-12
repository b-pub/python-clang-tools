#include "ignore_enums.hpp"

namespace person {
    namespace IDs {
        enum class Types {
            NONE = 100,
            PERSON_ONE,
            PERSON_TWO,
            PERSON_THREE,
            PERSON_FOUR,
        }
    }
}

namespace room {
    namespace IDs {
        namespace app {
            enum class Types {
                NONE = 200,
                ROOM_ONE,
                ROOM_TWO,
                ROOM_THREE,
                ROOM_FOUR,
            }
        }
    }
}

template <class T, int N>
class SomeClassWithTypesEnum {
    enum class Types {
        TENSOR,
        TRANSFORM,
        QUATERNION
    };
};

class AClassWithTypesEnum {
    enum class Types {
        TENSOR,
        TRANSFORM,
        QUATERNION
    };
};

